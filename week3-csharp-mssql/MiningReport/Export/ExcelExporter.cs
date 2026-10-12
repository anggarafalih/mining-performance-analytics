using ClosedXML.Excel;
using MiningReport.Models;

namespace MiningReport.Export;

public static class ExcelExporter
{
    public static string ExportReport(List<DailyPerformance> dailyRecords, List<BudgetVariance> variances, string outputDir)
    {
        Directory.CreateDirectory(outputDir);
        var filename = Path.Combine(outputDir, $"Laporan_Produksi_Tambang_{DateTime.Now:yyyyMMdd_HHmmss}.xlsx");

        using var workbook = new XLWorkbook();

        // 1. Sheet Ringkasan Varians
        var wsVariance = workbook.Worksheets.Add("Budget vs Actual");
        wsVariance.Cell(1, 1).Value = "LAPORAN SELISIH ANGGARAN BIAYA SOLAR (3-WAY VARIANCE)";
        wsVariance.Cell(1, 1).Style.Font.Bold = true;
        wsVariance.Cell(1, 1).Style.Font.FontSize = 14;

        var headersVar = new[] { "Bulan", "Site", "Nama Proyek", "Actual OB (BCM)", "Budget OB (BCM)", "Actual Solar (IDR)", "Budget Solar (IDR)", "Total Selisih (IDR)", "Volume Effect", "Efficiency Effect", "Price Effect" };
        for (int i = 0; i < headersVar.Length; i++)
        {
            var cell = wsVariance.Cell(3, i + 1);
            cell.Value = headersVar[i];
            cell.Style.Font.Bold = true;
            cell.Style.Fill.BackgroundColor = XLColor.FromArgb(27, 54, 93);
            cell.Style.Font.FontColor = XLColor.White;
        }

        int rowVar = 4;
        foreach (var v in variances)
        {
            wsVariance.Cell(rowVar, 1).Value = v.Month;
            wsVariance.Cell(rowVar, 2).Value = v.ProjectCode;
            wsVariance.Cell(rowVar, 3).Value = v.ProjectName;
            wsVariance.Cell(rowVar, 4).Value = v.ActualOverburdenBcm;
            wsVariance.Cell(rowVar, 5).Value = v.BudgetOverburdenBcm;
            wsVariance.Cell(rowVar, 6).Value = v.ActualFuelCostIdr;
            wsVariance.Cell(rowVar, 7).Value = v.BudgetFuelCostIdr;
            wsVariance.Cell(rowVar, 8).Value = v.TotalFuelCostVarianceIdr;
            wsVariance.Cell(rowVar, 9).Value = v.VolumeEffectIdr;
            wsVariance.Cell(rowVar, 10).Value = v.EfficiencyEffectIdr;
            wsVariance.Cell(rowVar, 11).Value = v.PriceEffectIdr;

            wsVariance.Cell(rowVar, 4).Style.NumberFormat.Format = "#,##0.0";
            wsVariance.Cell(rowVar, 5).Style.NumberFormat.Format = "#,##0.0";
            for (int col = 6; col <= 11; col++)
                wsVariance.Cell(rowVar, col).Style.NumberFormat.Format = "#,##0";

            rowVar++;
        }
        wsVariance.Columns().AdjustToContents();

        // 2. Sheet Harian
        var wsDaily = workbook.Worksheets.Add("Daily Performance");
        var headersDaily = new[] { "Tanggal", "Site", "Nama Proyek", "OB (BCM)", "Coal (Ton)", "Hujan (mm)", "Jam Kerja", "PA (%)", "UA (%)", "Fuel (Liter)" };
        for (int i = 0; i < headersDaily.Length; i++)
        {
            var cell = wsDaily.Cell(1, i + 1);
            cell.Value = headersDaily[i];
            cell.Style.Font.Bold = true;
            cell.Style.Fill.BackgroundColor = XLColor.FromArgb(27, 54, 93);
            cell.Style.Font.FontColor = XLColor.White;
        }

        int rowDaily = 2;
        foreach (var d in dailyRecords)
        {
            wsDaily.Cell(rowDaily, 1).Value = d.Date.ToString("yyyy-MM-dd");
            wsDaily.Cell(rowDaily, 2).Value = d.ProjectCode;
            wsDaily.Cell(rowDaily, 3).Value = d.ProjectName;
            wsDaily.Cell(rowDaily, 4).Value = d.OverburdenBcm;
            wsDaily.Cell(rowDaily, 5).Value = d.CoalTon;
            wsDaily.Cell(rowDaily, 6).Value = d.RainfallMm;
            wsDaily.Cell(rowDaily, 7).Value = d.HoursWorking;
            wsDaily.Cell(rowDaily, 8).Value = d.PhysicalAvailabilityPct / 100m;
            wsDaily.Cell(rowDaily, 9).Value = d.UtilizationPct / 100m;
            wsDaily.Cell(rowDaily, 10).Value = d.FuelLiter;

            wsDaily.Cell(rowDaily, 4).Style.NumberFormat.Format = "#,##0.0";
            wsDaily.Cell(rowDaily, 5).Style.NumberFormat.Format = "#,##0.0";
            wsDaily.Cell(rowDaily, 6).Style.NumberFormat.Format = "#,##0.0";
            wsDaily.Cell(rowDaily, 7).Style.NumberFormat.Format = "#,##0.0";
            wsDaily.Cell(rowDaily, 8).Style.NumberFormat.Format = "0.0%";
            wsDaily.Cell(rowDaily, 9).Style.NumberFormat.Format = "0.0%";
            wsDaily.Cell(rowDaily, 10).Style.NumberFormat.Format = "#,##0.0";

            rowDaily++;
        }
        wsDaily.Columns().AdjustToContents();

        workbook.SaveAs(filename);
        return filename;
    }
}
