namespace MiningReport.Models;

public class DailyPerformance
{
    public DateTime Date { get; set; }
    public string ProjectCode { get; set; } = string.Empty;
    public string ProjectName { get; set; } = string.Empty;
    public decimal OverburdenBcm { get; set; }
    public decimal CoalTon { get; set; }
    public decimal DailyTargetBcm { get; set; }
    public decimal DailyTargetCoal { get; set; }
    public decimal RainfallMm { get; set; }
    public decimal HoursWorking { get; set; }
    public decimal HoursStandby { get; set; }
    public decimal HoursBreakdown { get; set; }
    public decimal HoursAvailable { get; set; }
    public decimal FuelLiter { get; set; }
    public decimal FuelCostIdr { get; set; }
    public decimal PhysicalAvailabilityPct { get; set; }
    public decimal UtilizationPct { get; set; }
    public decimal ProductivityBcmPerHour { get; set; }
    public decimal FuelRatioLPerBcm { get; set; }
}

public class BudgetVariance
{
    public string Month { get; set; } = string.Empty; // YYYY-MM
    public string ProjectCode { get; set; } = string.Empty;
    public string ProjectName { get; set; } = string.Empty;
    public decimal ActualOverburdenBcm { get; set; }
    public decimal ActualCoalTon { get; set; }
    public decimal ActualFuelLiter { get; set; }
    public decimal ActualFuelCostIdr { get; set; }
    public decimal ActualFuelRatio { get; set; }
    public decimal ActualFuelPriceAvg { get; set; }
    public decimal BudgetOverburdenBcm { get; set; }
    public decimal BudgetCoalTon { get; set; }
    public decimal BudgetFuelLiter { get; set; }
    public decimal BudgetFuelCostIdr { get; set; }
    public decimal BudgetFuelRatio { get; set; }
    public decimal BudgetFuelPriceIdr { get; set; }
    public decimal TotalFuelCostVarianceIdr { get; set; }
    public decimal VolumeEffectIdr { get; set; }
    public decimal EfficiencyEffectIdr { get; set; }
    public decimal PriceEffectIdr { get; set; }
}
