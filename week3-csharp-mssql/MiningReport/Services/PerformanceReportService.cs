using System.Globalization;
using MiningReport.Data;
using MiningReport.Models;

namespace MiningReport.Services;

public class PerformanceReportService
{
    private readonly PerformanceRepository _repository;

    public PerformanceReportService(PerformanceRepository repository)
    {
        _repository = repository;
    }

    public async Task PrintDailySummaryAsync(DateTime? startDate, DateTime? endDate, string? projectCode)
    {
        var records = await _repository.GetDailyPerformanceAsync(startDate, endDate, projectCode);
        Console.WriteLine("\n=========================================================================================");
        Console.WriteLine($"RINGKASAN PRODUKSI HARIAN ({records.Count} Catatan Ditemukan)");
        Console.WriteLine("=========================================================================================");
        Console.WriteLine("{0,-12} {1,-8} {2,14} {3,12} {4,8} {5,8} {6,10}", "Tanggal", "Proyek", "OB (BCM)", "Coal (Ton)", "PA (%)", "UA (%)", "Fuel (L)");
        Console.WriteLine(new string('-', 89));

        foreach (var r in records.Take(15))
        {
            Console.WriteLine("{0,-12} {1,-8} {2,14:N1} {3,12:N1} {4,8:N1} {5,8:N1} {6,10:N1}",
                r.Date.ToString("yyyy-MM-dd"), r.ProjectCode, r.OverburdenBcm, r.CoalTon,
                r.PhysicalAvailabilityPct, r.UtilizationPct, r.FuelLiter);
        }

        if (records.Count > 15)
        {
            Console.WriteLine($"... dan {records.Count - 15} baris lainnya.");
        }

        var totalOb = records.Sum(r => r.OverburdenBcm);
        var totalCoal = records.Sum(r => r.CoalTon);
        var totalFuel = records.Sum(r => r.FuelLiter);
        Console.WriteLine(new string('=', 89));
        Console.WriteLine($"TOTAL TERPILIH -> Overburden: {totalOb:N1} BCM | Batubara: {totalCoal:N1} Ton | Solar: {totalFuel:N1} Liter\n");
    }

    public async Task PrintMonthlySummaryAsync(string? projectCode)
    {
        var variances = await _repository.GetMonthlyVarianceAsync(projectCode);
        Console.WriteLine("\n=========================================================================================");
        Console.WriteLine("RINGKASAN PRODUKSI BULANAN & PENCAPAIAN TARGET");
        Console.WriteLine("=========================================================================================");
        Console.WriteLine("{0,-8} {1,-6} {2,14} {3,14} {4,10} {5,12}", "Bulan", "Site", "Actual OB", "Budget OB", "Capai (%)", "Fuel Ratio");
        Console.WriteLine(new string('-', 76));

        foreach (var v in variances)
        {
            var ach = MetricsCalculator.CalculateTargetAchievement(v.ActualOverburdenBcm, v.BudgetOverburdenBcm);
            Console.WriteLine("{0,-8} {1,-6} {2,14:N0} {3,14:N0} {4,9:N1}% {5,12:N3}",
                v.Month, v.ProjectCode, v.ActualOverburdenBcm, v.BudgetOverburdenBcm, ach, v.ActualFuelRatio);
        }
        Console.WriteLine(new string('=', 76) + "\n");
    }

    public async Task PrintVarianceAnalysisAsync(string? projectCode)
    {
        var variances = await _repository.GetMonthlyVarianceAsync(projectCode);
        Console.WriteLine("\n==========================================================================================================");
        Console.WriteLine("ANALISIS VARIANS BIAYA SOLAR (3-WAY DECOMPOSITION: VOLUME, EFISIENSI, HARGA)");
        Console.WriteLine("==========================================================================================================");
        Console.WriteLine("{0,-8} {1,-6} {2,18} {3,18} {4,18} {5,18}", "Bulan", "Site", "Total Var (IDR)", "Volume Eff (IDR)", "Eff Eff (IDR)", "Price Eff (IDR)");
        Console.WriteLine(new string('-', 106));

        foreach (var v in variances)
        {
            Console.WriteLine("{0,-8} {1,-6} {2,18:N0} {3,18:N0} {4,18:N0} {5,18:N0}",
                v.Month, v.ProjectCode, v.TotalFuelCostVarianceIdr, v.VolumeEffectIdr, v.EfficiencyEffectIdr, v.PriceEffectIdr);
        }

        var totVar = variances.Sum(v => v.TotalFuelCostVarianceIdr);
        var totVol = variances.Sum(v => v.VolumeEffectIdr);
        var totEff = variances.Sum(v => v.EfficiencyEffectIdr);
        var totPrc = variances.Sum(v => v.PriceEffectIdr);

        Console.WriteLine(new string('=', 106));
        Console.WriteLine("{0,-15} {1,18:N0} {2,18:N0} {3,18:N0} {4,18:N0}",
            "TOTAL TAHUNAN", totVar, totVol, totEff, totPrc);
        Console.WriteLine($"Validasi Residu: |(Vol + Eff + Prc) - Tot| = {Math.Abs((totVol + totEff + totPrc) - totVar):N4} IDR (0 = Match)\n");
    }
}
