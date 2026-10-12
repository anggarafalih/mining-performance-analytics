using System.Globalization;
using MiningReport.Data;
using MiningReport.Export;
using MiningReport.Services;

namespace MiningReport;

public class Program
{
    public static async Task<int> Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("=================================================================");
        Console.WriteLine("MINING PRODUCTION PERFORMANCE ANALYTICS (.NET 8 CLI)");
        Console.WriteLine("Studi Kasus Portofolio Operasional Tambang - PT PAMA Standard");
        Console.WriteLine("=================================================================");

        var config = DatabaseConfig.Load();
        var repository = new PerformanceRepository(config.ConnectionString);
        var reportService = new PerformanceReportService(repository);

        if (args.Length == 0)
        {
            PrintUsage();
            return 0;
        }

        var command = args[0].ToLowerInvariant();
        var namedArgs = ParseArguments(args.Skip(1).ToArray());

        try
        {
            switch (command)
            {
                case "daily":
                {
                    DateTime? start = null;
                    DateTime? end = null;
                    if (namedArgs.TryGetValue("start", out var s) && DateTime.TryParse(s, CultureInfo.InvariantCulture, out var dtStart))
                        start = dtStart;
                    if (namedArgs.TryGetValue("end", out var e) && DateTime.TryParse(e, CultureInfo.InvariantCulture, out var dtEnd))
                        end = dtEnd;
                    namedArgs.TryGetValue("project", out var prj);

                    await reportService.PrintDailySummaryAsync(start, end, prj);
                    return 0;
                }

                case "monthly":
                {
                    namedArgs.TryGetValue("project", out var prj);
                    await reportService.PrintMonthlySummaryAsync(prj);
                    return 0;
                }

                case "variance":
                {
                    namedArgs.TryGetValue("project", out var prj);
                    await reportService.PrintVarianceAnalysisAsync(prj);
                    return 0;
                }

                case "export":
                {
                    var outDir = namedArgs.GetValueOrDefault("output", "output");
                    Console.WriteLine($"\nMengekstrak data dan mengekspor laporan ke folder: {outDir}...");

                    var daily = await repository.GetDailyPerformanceAsync();
                    var variance = await repository.GetMonthlyVarianceAsync();

                    var csvDaily = CsvExporter.ExportDaily(daily, outDir);
                    var csvVar = CsvExporter.ExportVariance(variance, outDir);
                    var xlsx = ExcelExporter.ExportReport(daily, variance, outDir);

                    Console.WriteLine($"[V] Berhasil diekspor:");
                    Console.WriteLine($"  - CSV Harian  : {csvDaily}");
                    Console.WriteLine($"  - CSV Varians : {csvVar}");
                    Console.WriteLine($"  - Excel Report: {xlsx}\n");
                    return 0;
                }

                case "help":
                case "--help":
                case "-h":
                    PrintUsage();
                    return 0;

                default:
                    Console.ForegroundColor = ConsoleColor.Red;
                    Console.WriteLine($"[!] Perintah '{command}' tidak dikenali.");
                    Console.ResetColor();
                    PrintUsage();
                    return 1;
            }
        }
        catch (Exception ex)
        {
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine($"[!] Terjadi kesalahan saat menjalankan perintah: {ex.Message}");
            Console.ResetColor();
            return 1;
        }
    }

    private static void PrintUsage()
    {
        Console.WriteLine("\nPenggunaan CLI:");
        Console.WriteLine("  MiningReport <command> [options]\n");
        Console.WriteLine("Perintah yang tersedia:");
        Console.WriteLine("  daily     : Menampilkan ringkasan produksi harian");
        Console.WriteLine("              Opsi: --start YYYY-MM-DD --end YYYY-MM-DD --project P01..P04");
        Console.WriteLine("  monthly   : Menampilkan ringkasan bulanan dan pencapaian target");
        Console.WriteLine("              Opsi: --project P01..P04");
        Console.WriteLine("  variance  : Menampilkan analisis selisih anggaran biaya (3-way decomposition)");
        Console.WriteLine("              Opsi: --project P01..P04");
        Console.WriteLine("  export    : Mengekspor seluruh laporan ke CSV dan Excel di folder output/");
        Console.WriteLine("              Opsi: --output <direktori>");
        Console.WriteLine("\nContoh:");
        Console.WriteLine("  MiningReport daily --start 2025-01-01 --end 2025-01-15 --project P01");
        Console.WriteLine("  MiningReport variance --project P03");
        Console.WriteLine("  MiningReport export\n");
    }

    private static Dictionary<string, string> ParseArguments(string[] args)
    {
        var dict = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        for (int i = 0; i < args.Length; i++)
        {
            if (args[i].StartsWith("--") && i + 1 < args.Length)
            {
                var key = args[i].TrimStart('-');
                var val = args[i + 1];
                dict[key] = val;
                i++;
            }
        }
        return dict;
    }
}
