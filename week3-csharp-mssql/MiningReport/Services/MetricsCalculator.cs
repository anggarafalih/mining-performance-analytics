namespace MiningReport.Services;

public static class MetricsCalculator
{
    public static decimal CalculatePhysicalAvailability(decimal hoursAvailable, decimal hoursBreakdown)
    {
        if (hoursAvailable <= 0) return 0m;
        var pa = ((hoursAvailable - hoursBreakdown) / hoursAvailable) * 100m;
        return Math.Round(Math.Max(0m, Math.Min(100m, pa)), 2);
    }

    public static decimal CalculateUtilization(decimal hoursWorking, decimal hoursAvailable)
    {
        if (hoursAvailable <= 0) return 0m;
        var ut = (hoursWorking / hoursAvailable) * 100m;
        return Math.Round(Math.Max(0m, Math.Min(100m, ut)), 2);
    }

    public static decimal CalculateProductivity(decimal overburdenBcm, decimal hoursWorking)
    {
        if (hoursWorking <= 0) return 0m;
        return Math.Round(overburdenBcm / hoursWorking, 2);
    }

    public static decimal CalculateFuelRatio(decimal fuelLiter, decimal overburdenBcm, bool round = true)
    {
        if (overburdenBcm <= 0) return 0m;
        var ratio = fuelLiter / overburdenBcm;
        return round ? Math.Round(ratio, 3) : ratio;
    }

    public static decimal CalculateTargetAchievement(decimal actualValue, decimal targetValue)
    {
        if (targetValue <= 0) return 0m;
        return Math.Round((actualValue / targetValue) * 100m, 2);
    }

    public static decimal CalculateVolumeEffect(decimal actualBcm, decimal budgetBcm, decimal budgetFuelRatio, decimal budgetPrice)
    {
        return Math.Round((actualBcm - budgetBcm) * budgetFuelRatio * budgetPrice, 2);
    }

    public static decimal CalculateEfficiencyEffect(decimal actualBcm, decimal actualFuelRatio, decimal budgetFuelRatio, decimal budgetPrice)
    {
        return Math.Round(actualBcm * (actualFuelRatio - budgetFuelRatio) * budgetPrice, 2);
    }

    public static decimal CalculatePriceEffect(decimal actualBcm, decimal actualFuelRatio, decimal actualPrice, decimal budgetPrice)
    {
        return Math.Round(actualBcm * actualFuelRatio * (actualPrice - budgetPrice), 2);
    }

    public static decimal CalculateTotalVariance(decimal actualCost, decimal budgetCost)
    {
        return Math.Round(actualCost - budgetCost, 2);
    }

    public static bool VerifyVarianceDecomposition(decimal volumeEffect, decimal efficiencyEffect, decimal priceEffect, decimal totalVariance, decimal tolerance = 1.0m)
    {
        var sum = volumeEffect + efficiencyEffect + priceEffect;
        return Math.Abs(sum - totalVariance) <= tolerance;
    }
}
