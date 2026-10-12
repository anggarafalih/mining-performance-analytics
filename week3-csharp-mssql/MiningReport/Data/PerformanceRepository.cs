using System.Data;
using System.Globalization;
using Dapper;
using Microsoft.Data.SqlClient;
using MiningReport.Models;
using MiningReport.Services;

namespace MiningReport.Data;

public class PerformanceRepository
{
    private readonly string _connectionString;

    public PerformanceRepository(string connectionString)
    {
        _connectionString = connectionString;
    }

    public bool TestConnection(out string message)
    {
        try
        {
            using var conn = new SqlConnection(_connectionString);
            conn.Open();
            message = "Koneksi ke SQL Server berhasil terhubung.";
            return true;
        }
        catch (Exception ex)
        {
            message = $"Gagal terhubung ke SQL Server: {ex.Message}";
            return false;
        }
    }

    public async Task<List<DailyPerformance>> GetDailyPerformanceAsync(DateTime? startDate = null, DateTime? endDate = null, string? projectCode = null)
    {
        if (TestConnection(out _))
        {
            using var conn = new SqlConnection(_connectionString);
            var sql = @"
                SELECT * FROM dbo.v_daily_performance 
                WHERE (@StartDate IS NULL OR date >= @StartDate)
                  AND (@EndDate IS NULL OR date <= @EndDate)
                  AND (@ProjectCode IS NULL OR project_code = @ProjectCode)
                ORDER BY date, project_code;";

            var records = await conn.QueryAsync<DailyPerformance>(sql, new { StartDate = startDate, EndDate = endDate, ProjectCode = projectCode });
            return records.AsList();
        }

        // Graceful fallback to Master CSV
        return LoadDailyPerformanceFromCsv(startDate, endDate, projectCode);
    }

    public async Task<List<BudgetVariance>> GetMonthlyVarianceAsync(string? projectCode = null)
    {
        if (TestConnection(out _))
        {
            using var conn = new SqlConnection(_connectionString);
            var sql = @"
                SELECT * FROM dbo.v_monthly_variance 
                WHERE (@ProjectCode IS NULL OR project_code = @ProjectCode)
                ORDER BY project_code, month;";

            var records = await conn.QueryAsync<BudgetVariance>(sql, new { ProjectCode = projectCode });
            return records.AsList();
        }

        // Graceful fallback to Master CSV
        return LoadMonthlyVarianceFromCsv(projectCode);
    }

    private static string FindDataDir()
    {
        var candidates = new[] { "data", "../data", "../../data", "../../../data", "../../../../data" };
        foreach (var dir in candidates)
        {
            if (File.Exists(Path.Combine(dir, "fact_production.csv")))
                return Path.GetFullPath(dir);
        }
        return "data";
    }

    private static List<DailyPerformance> LoadDailyPerformanceFromCsv(DateTime? startDate, DateTime? endDate, string? projectCode)
    {
        var dataDir = FindDataDir();
        var prodFile = Path.Combine(dataDir, "fact_production.csv");
        var projFile = Path.Combine(dataDir, "dim_project.csv");
        var eqFile = Path.Combine(dataDir, "dim_equipment.csv");
        var hoursFile = Path.Combine(dataDir, "fact_equipment_hours.csv");
        var fuelFile = Path.Combine(dataDir, "fact_fuel.csv");

        var projects = File.ReadAllLines(projFile).Skip(1)
            .Select(l => l.Split(','))
            .ToDictionary(p => p[0], p => p[1]);

        var eqProjects = File.ReadAllLines(eqFile).Skip(1)
            .Select(l => l.Split(','))
            .ToDictionary(e => e[0], e => e[2]);

        // Aggregate hours by date and project
        var hoursMap = new Dictionary<(string Date, string Project), (decimal Wk, decimal St, decimal Br, decimal Av)>();
        foreach (var line in File.ReadAllLines(hoursFile).Skip(1))
        {
            var p = line.Split(',');
            var dt = p[0];
            var eq = p[1];
            if (!eqProjects.TryGetValue(eq, out var prj)) continue;
            var wk = decimal.Parse(p[2], CultureInfo.InvariantCulture);
            var st = decimal.Parse(p[3], CultureInfo.InvariantCulture);
            var br = decimal.Parse(p[4], CultureInfo.InvariantCulture);
            var av = decimal.Parse(p[5], CultureInfo.InvariantCulture);

            var key = (dt, prj);
            if (!hoursMap.ContainsKey(key))
                hoursMap[key] = (0, 0, 0, 0);
            var cur = hoursMap[key];
            hoursMap[key] = (cur.Wk + wk, cur.St + st, cur.Br + br, cur.Av + av);
        }

        // Aggregate fuel by date and project
        var fuelMap = new Dictionary<(string Date, string Project), (decimal Liters, decimal Cost)>();
        foreach (var line in File.ReadAllLines(fuelFile).Skip(1))
        {
            var p = line.Split(',');
            var dt = p[0];
            var eq = p[1];
            if (!eqProjects.TryGetValue(eq, out var prj)) continue;
            var lit = decimal.Parse(p[2], CultureInfo.InvariantCulture);
            var prc = decimal.Parse(p[3], CultureInfo.InvariantCulture);

            var key = (dt, prj);
            if (!fuelMap.ContainsKey(key))
                fuelMap[key] = (0, 0);
            var cur = fuelMap[key];
            fuelMap[key] = (cur.Liters + lit, cur.Cost + (lit * prc));
        }

        var result = new List<DailyPerformance>();
        foreach (var line in File.ReadAllLines(prodFile).Skip(1))
        {
            var p = line.Split(',');
            var dt = DateTime.Parse(p[0], CultureInfo.InvariantCulture);
            var dtStr = p[0];
            var prj = p[1];

            if (startDate.HasValue && dt < startDate.Value) continue;
            if (endDate.HasValue && dt > endDate.Value) continue;
            if (!string.IsNullOrEmpty(projectCode) && !string.Equals(prj, projectCode, StringComparison.OrdinalIgnoreCase)) continue;

            var ob = decimal.Parse(p[2], CultureInfo.InvariantCulture);
            var coal = decimal.Parse(p[3], CultureInfo.InvariantCulture);
            var tOb = decimal.Parse(p[4], CultureInfo.InvariantCulture);
            var tCoal = decimal.Parse(p[5], CultureInfo.InvariantCulture);
            var rain = decimal.Parse(p[6], CultureInfo.InvariantCulture);

            var key = (dtStr, prj);
            var (wk, st, br, av) = hoursMap.GetValueOrDefault(key, (0, 0, 0, 0));
            var (fuelLit, fuelCost) = fuelMap.GetValueOrDefault(key, (0, 0));

            result.Add(new DailyPerformance
            {
                Date = dt,
                ProjectCode = prj,
                ProjectName = projects.GetValueOrDefault(prj, prj),
                OverburdenBcm = ob,
                CoalTon = coal,
                DailyTargetBcm = tOb,
                DailyTargetCoal = tCoal,
                RainfallMm = rain,
                HoursWorking = wk,
                HoursStandby = st,
                HoursBreakdown = br,
                HoursAvailable = av,
                FuelLiter = fuelLit,
                FuelCostIdr = fuelCost,
                PhysicalAvailabilityPct = MetricsCalculator.CalculatePhysicalAvailability(av, br),
                UtilizationPct = MetricsCalculator.CalculateUtilization(wk, av),
                ProductivityBcmPerHour = MetricsCalculator.CalculateProductivity(ob, wk),
                FuelRatioLPerBcm = MetricsCalculator.CalculateFuelRatio(fuelLit, ob)
            });
        }

        return result;
    }

    private static List<BudgetVariance> LoadMonthlyVarianceFromCsv(string? projectCode)
    {
        var daily = LoadDailyPerformanceFromCsv(null, null, projectCode);
        var dataDir = FindDataDir();
        var budgetFile = Path.Combine(dataDir, "budget_monthly.csv");

        var monthlyActuals = daily
            .GroupBy(d => new { Month = d.Date.ToString("yyyy-MM"), d.ProjectCode, d.ProjectName })
            .Select(g => new
            {
                g.Key.Month,
                g.Key.ProjectCode,
                g.Key.ProjectName,
                ActualOb = g.Sum(x => x.OverburdenBcm),
                ActualCoal = g.Sum(x => x.CoalTon),
                ActualFuelLiter = g.Sum(x => x.FuelLiter),
                ActualFuelCost = g.Sum(x => x.FuelCostIdr)
            })
            .ToDictionary(k => (k.Month, k.ProjectCode));

        var result = new List<BudgetVariance>();
        foreach (var line in File.ReadAllLines(budgetFile).Skip(1))
        {
            var p = line.Split(',');
            var m = p[0];
            var prj = p[1];
            if (!string.IsNullOrEmpty(projectCode) && !string.Equals(prj, projectCode, StringComparison.OrdinalIgnoreCase)) continue;

            var tOb = decimal.Parse(p[2], CultureInfo.InvariantCulture);
            var tCoal = decimal.Parse(p[3], CultureInfo.InvariantCulture);
            var bFuelLit = decimal.Parse(p[4], CultureInfo.InvariantCulture);
            var bFuelPrice = decimal.Parse(p[5], CultureInfo.InvariantCulture);
            var bFuelCost = decimal.Parse(p[6], CultureInfo.InvariantCulture);

            if (!monthlyActuals.TryGetValue((m, prj), out var act)) continue;

            var actRatio = MetricsCalculator.CalculateFuelRatio(act.ActualFuelLiter, act.ActualOb, round: false);
            var bgtRatio = MetricsCalculator.CalculateFuelRatio(bFuelLit, tOb, round: false);
            var actPrice = act.ActualFuelLiter > 0 ? act.ActualFuelCost / act.ActualFuelLiter : 0m;

            var volEff = MetricsCalculator.CalculateVolumeEffect(act.ActualOb, tOb, bgtRatio, bFuelPrice);
            var effEff = MetricsCalculator.CalculateEfficiencyEffect(act.ActualOb, actRatio, bgtRatio, bFuelPrice);
            var prcEff = MetricsCalculator.CalculatePriceEffect(act.ActualOb, actRatio, actPrice, bFuelPrice);
            var totVar = MetricsCalculator.CalculateTotalVariance(act.ActualFuelCost, bFuelCost);

            result.Add(new BudgetVariance
            {
                Month = m,
                ProjectCode = prj,
                ProjectName = act.ProjectName,
                ActualOverburdenBcm = act.ActualOb,
                ActualCoalTon = act.ActualCoal,
                ActualFuelLiter = act.ActualFuelLiter,
                ActualFuelCostIdr = act.ActualFuelCost,
                ActualFuelRatio = Math.Round(actRatio, 3),
                ActualFuelPriceAvg = Math.Round(actPrice, 2),
                BudgetOverburdenBcm = tOb,
                BudgetCoalTon = tCoal,
                BudgetFuelLiter = bFuelLit,
                BudgetFuelCostIdr = bFuelCost,
                BudgetFuelRatio = Math.Round(bgtRatio, 3),
                BudgetFuelPriceIdr = bFuelPrice,
                TotalFuelCostVarianceIdr = totVar,
                VolumeEffectIdr = volEff,
                EfficiencyEffectIdr = effEff,
                PriceEffectIdr = prcEff
            });
        }

        return result.OrderBy(r => r.ProjectCode).ThenBy(r => r.Month).ToList();
    }
}
