using MiningReport.Services;
using Xunit;

namespace MiningReport.Tests;

public class PerformanceMetricsTests
{
    [Fact]
    public void CalculatePhysicalAvailability_ValidInputs_ReturnsExpectedPercentage()
    {
        // Arrange: 24 jam kalender, 2 jam breakdown -> (24 - 2) / 24 = 91.67%
        decimal hoursAvailable = 24.0m;
        decimal hoursBreakdown = 2.0m;

        // Act
        var pa = MetricsCalculator.CalculatePhysicalAvailability(hoursAvailable, hoursBreakdown);

        // Assert
        Assert.Equal(91.67m, pa);
    }

    [Fact]
    public void CalculatePhysicalAvailability_ZeroAvailableHours_ReturnsZero()
    {
        // Arrange
        decimal hoursAvailable = 0.0m;
        decimal hoursBreakdown = 0.0m;

        // Act
        var pa = MetricsCalculator.CalculatePhysicalAvailability(hoursAvailable, hoursBreakdown);

        // Assert
        Assert.Equal(0.0m, pa);
    }

    [Fact]
    public void CalculateUtilization_ValidInputs_ReturnsExpectedPercentage()
    {
        // Arrange: 15 jam working dari 24 jam tersedia -> 15 / 24 = 62.5%
        decimal hoursWorking = 15.0m;
        decimal hoursAvailable = 24.0m;

        // Act
        var ut = MetricsCalculator.CalculateUtilization(hoursWorking, hoursAvailable);

        // Assert
        Assert.Equal(62.5m, ut);
    }

    [Fact]
    public void CalculateProductivity_ValidInputs_ReturnsCorrectBcmPerHour()
    {
        // Arrange: 40,000 BCM dikerjakan dalam 16 jam -> 2,500 BCM/jam
        decimal bcm = 40000m;
        decimal hoursWorking = 16.0m;

        // Act
        var prod = MetricsCalculator.CalculateProductivity(bcm, hoursWorking);

        // Assert
        Assert.Equal(2500.0m, prod);
    }

    [Fact]
    public void CalculateFuelRatio_ValidInputs_ReturnsLitersPerBcm()
    {
        // Arrange: 68,000 Liter untuk 40,000 BCM -> 1.700 L/BCM
        decimal fuelLiter = 68000m;
        decimal bcm = 40000m;

        // Act
        var ratio = MetricsCalculator.CalculateFuelRatio(fuelLiter, bcm);

        // Assert
        Assert.Equal(1.700m, ratio);
    }

    [Fact]
    public void CalculateTargetAchievement_ValidInputs_ReturnsPercentage()
    {
        // Arrange: Actual 38,000 BCM, Target 40,000 BCM -> 95.0%
        decimal actual = 38000m;
        decimal target = 40000m;

        // Act
        var ach = MetricsCalculator.CalculateTargetAchievement(actual, target);

        // Assert
        Assert.Equal(95.0m, ach);
    }

    [Fact]
    public void CalculateVolumeEffect_ValidInputs_ComputesExpectedIDR()
    {
        // Arrange: Actual 90,000 BCM, Budget 100,000 BCM, Budget Ratio 1.8, Budget Price 14,500 IDR
        // Vol Effect = (90k - 100k) * 1.8 * 14,500 = -10,000 * 26,100 = -261,000,000 IDR
        decimal actualBcm = 90000m;
        decimal budgetBcm = 100000m;
        decimal budgetRatio = 1.8m;
        decimal budgetPrice = 14500m;

        // Act
        var volEffect = MetricsCalculator.CalculateVolumeEffect(actualBcm, budgetBcm, budgetRatio, budgetPrice);

        // Assert
        Assert.Equal(-261000000m, volEffect);
    }

    [Fact]
    public void CalculateEfficiencyEffect_ValidInputs_ComputesExpectedIDR()
    {
        // Arrange: Actual 90,000 BCM, Actual Ratio 2.0, Budget Ratio 1.8, Budget Price 14,500 IDR
        // Eff Effect = 90k * (2.0 - 1.8) * 14,500 = 90k * 0.2 * 14,500 = +261,000,000 IDR (pemborosan)
        decimal actualBcm = 90000m;
        decimal actualRatio = 2.0m;
        decimal budgetRatio = 1.8m;
        decimal budgetPrice = 14500m;

        // Act
        var effEffect = MetricsCalculator.CalculateEfficiencyEffect(actualBcm, actualRatio, budgetRatio, budgetPrice);

        // Assert
        Assert.Equal(261000000m, effEffect);
    }

    [Fact]
    public void CalculatePriceEffect_ValidInputs_ComputesExpectedIDR()
    {
        // Arrange: Actual 90,000 BCM, Actual Ratio 2.0, Actual Price 15,000, Budget Price 14,500
        // Prc Effect = 90k * 2.0 * (15,000 - 14,500) = 180k * 500 = +90,000,000 IDR
        decimal actualBcm = 90000m;
        decimal actualRatio = 2.0m;
        decimal actualPrice = 15000m;
        decimal budgetPrice = 14500m;

        // Act
        var prcEffect = MetricsCalculator.CalculatePriceEffect(actualBcm, actualRatio, actualPrice, budgetPrice);

        // Assert
        Assert.Equal(90000000m, prcEffect);
    }

    [Fact]
    public void VarianceDecomposition_SumOfThreeEffects_MatchesTotalVarianceExactly()
    {
        // Mathematical proof of 3-way decomposition:
        // Total Variance = Actual Fuel Cost - Budget Fuel Cost
        // = (Actual BCM * Actual Ratio * Actual Price) - (Budget BCM * Budget Ratio * Budget Price)
        decimal actualBcm = 1200000m;
        decimal budgetBcm = 1300000m;
        decimal actualRatio = 1.75m;
        decimal budgetRatio = 1.80m;
        decimal actualPrice = 15200m;
        decimal budgetPrice = 14500m;

        decimal actualFuelCost = actualBcm * actualRatio * actualPrice;
        decimal budgetFuelCost = budgetBcm * budgetRatio * budgetPrice;
        decimal totalVariance = MetricsCalculator.CalculateTotalVariance(actualFuelCost, budgetFuelCost);

        decimal volEffect = MetricsCalculator.CalculateVolumeEffect(actualBcm, budgetBcm, budgetRatio, budgetPrice);
        decimal effEffect = MetricsCalculator.CalculateEfficiencyEffect(actualBcm, actualRatio, budgetRatio, budgetPrice);
        decimal prcEffect = MetricsCalculator.CalculatePriceEffect(actualBcm, actualRatio, actualPrice, budgetPrice);

        // Verify decomposition
        var isValid = MetricsCalculator.VerifyVarianceDecomposition(volEffect, effEffect, prcEffect, totalVariance);

        Assert.True(isValid);
        Assert.Equal(totalVariance, volEffect + effEffect + prcEffect);
    }
}
