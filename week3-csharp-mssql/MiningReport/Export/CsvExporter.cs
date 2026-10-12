using System.Globalization;
using System.Text;
using MiningReport.Models;

namespace MiningReport.Export;

public static class CsvExporter
{
    public static string ExportDaily(List<DailyPerformance> records, string outputDir)
    {
        Directory.CreateDirectory(outputDir);
        var filename = Path.Combine(outputDir, $"Laporan_Harian_{DateTime.Now:yyyyMMdd_HHmmss}.csv");
        var sb = new StringBuilder();

        sb.AppendLine("Date,ProjectCode,ProjectName,OverburdenBcm,CoalTon,DailyTargetBcm,RainfallMm,HoursWorking,HoursStandby,HoursBreakdown,HoursAvailable,FuelLiter,FuelCostIdr,PhysicalAvailabilityPct,UtilizationPct,ProductivityBcmPerHour,FuelRatioLPerBcm");
        foreach (var r in records)
        {
            sb.AppendLine(string.Format(CultureInfo.InvariantCulture,
                "{0:yyyy-MM-dd},{1},{2},{3:F1},{4:F1},{5:F1},{6:F1},{7:F1},{8:F1},{9:F1},{10:F1},{11:F1},{12:F0},{13:F2},{14:F2},{15:F2},{16:F3}",
                r.Date, r.ProjectCode, r.ProjectName, r.OverburdenBcm, r.CoalTon, r.DailyTargetBcm, r.RainfallMm,
                r.HoursWorking, r.HoursStandby, r.HoursBreakdown, r.HoursAvailable, r.FuelLiter, r.FuelCostIdr,
                r.PhysicalAvailabilityPct, r.UtilizationPct, r.ProductivityBcmPerHour, r.FuelRatioLPerBcm));
        }

        File.WriteAllText(filename, sb.ToString());
        return filename;
    }

    public static string ExportVariance(List<BudgetVariance> variances, string outputDir)
    {
        Directory.CreateDirectory(outputDir);
        var filename = Path.Combine(outputDir, $"Laporan_Varians_{DateTime.Now:yyyyMMdd_HHmmss}.csv");
        var sb = new StringBuilder();

        sb.AppendLine("Month,ProjectCode,ProjectName,ActualOverburdenBcm,BudgetOverburdenBcm,ActualFuelCostIdr,BudgetFuelCostIdr,TotalFuelCostVarianceIdr,VolumeEffectIdr,EfficiencyEffectIdr,PriceEffectIdr");
        foreach (var v in variances)
        {
            sb.AppendLine(string.Format(CultureInfo.InvariantCulture,
                "{0},{1},{2},{3:F1},{4:F1},{5:F0},{6:F0},{7:F0},{8:F0},{9:F0},{10:F0}",
                v.Month, v.ProjectCode, v.ProjectName, v.ActualOverburdenBcm, v.BudgetOverburdenBcm,
                v.ActualFuelCostIdr, v.BudgetFuelCostIdr, v.TotalFuelCostVarianceIdr,
                v.VolumeEffectIdr, v.EfficiencyEffectIdr, v.PriceEffectIdr));
        }

        File.WriteAllText(filename, sb.ToString());
        return filename;
    }
}
