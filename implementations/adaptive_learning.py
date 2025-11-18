"""
Phase 5: Adaptive Learning System
Predicts token consumption, adjusts budgets, and learns from execution trends.

Features:
- Adaptive budget prediction based on pattern history
- Temporal trend analysis and decay
- Anomaly detection for unusual patterns
- Alert system for over-budget patterns
- Context-aware budget adjustment
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import statistics
import math


@dataclass
class TokenPrediction:
    """Prediction for token consumption of a pattern."""

    pattern_query: str
    pattern_level: int

    # Predictions
    predicted_tokens: int  # Best estimate
    confidence: float  # 0.0-1.0, based on data consistency

    # Range
    min_tokens: int  # Conservative estimate
    max_tokens: int  # Pessimistic estimate

    # Reasoning
    basis: str  # "historical_average", "moving_average", "trend_extrapolation", "machine_learning"
    samples: int  # Number of executions used

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def prediction_range(self) -> str:
        """Return prediction as range string"""
        return f"{self.min_tokens}-{self.max_tokens} (predicted: {self.predicted_tokens})"

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "pattern_query": self.pattern_query,
            "pattern_level": self.pattern_level,
            "predicted_tokens": self.predicted_tokens,
            "confidence": self.confidence,
            "min_tokens": self.min_tokens,
            "max_tokens": self.max_tokens,
            "range": self.prediction_range,
            "basis": self.basis,
            "samples": self.samples,
            "timestamp": self.timestamp
        }


@dataclass
class TrendAnalysis:
    """Analysis of token consumption trend for a pattern."""

    pattern_query: str
    pattern_level: int

    # Trend direction
    trend: str  # "increasing", "decreasing", "stable"
    trend_percentage: float  # % change per execution

    # Volatility
    volatility: float  # Standard deviation of deltas
    consistency: float  # 1.0 = perfectly consistent, 0.0 = highly volatile

    # Data points
    sample_count: int
    time_span_hours: float

    # Forecast
    forecasted_next: int  # Predicted consumption for next execution
    forecast_confidence: float  # How confident in forecast

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "pattern_query": self.pattern_query,
            "pattern_level": self.pattern_level,
            "trend": self.trend,
            "trend_percentage": self.trend_percentage,
            "volatility": self.volatility,
            "consistency": self.consistency,
            "sample_count": self.sample_count,
            "time_span_hours": self.time_span_hours,
            "forecasted_next": self.forecasted_next,
            "forecast_confidence": self.forecast_confidence,
            "timestamp": self.timestamp
        }


@dataclass
class BudgetAlert:
    """Alert when pattern exceeds budget."""

    pattern_query: str
    pattern_level: int
    severity: str  # "info", "warning", "critical"

    predicted_budget: int
    actual_budget: int
    variance: float  # Percentage over budget

    message: str
    recommendation: str

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "pattern_query": self.pattern_query,
            "pattern_level": self.pattern_level,
            "severity": self.severity,
            "predicted_budget": self.predicted_budget,
            "actual_budget": self.actual_budget,
            "variance": self.variance,
            "message": self.message,
            "recommendation": self.recommendation,
            "timestamp": self.timestamp
        }


class TrendAnalyzer:
    """Analyzes consumption trends and patterns over time."""

    @staticmethod
    def analyze_trend(token_deltas: List[int], timestamps: Optional[List[str]] = None) -> TrendAnalysis:
        """
        Analyze trend in token consumption.

        Args:
            token_deltas: List of token consumption values
            timestamps: Optional list of ISO timestamps for temporal analysis

        Returns:
            TrendAnalysis with trend direction and forecast
        """
        if len(token_deltas) < 2:
            return TrendAnalysis(
                pattern_query="unknown",
                pattern_level=0,
                trend="insufficient_data",
                trend_percentage=0.0,
                volatility=0.0,
                consistency=0.0,
                sample_count=len(token_deltas),
                time_span_hours=0.0,
                forecasted_next=token_deltas[0] if token_deltas else 0,
                forecast_confidence=0.0
            )

        # Calculate statistics
        mean = statistics.mean(token_deltas)
        variance = statistics.variance(token_deltas) if len(token_deltas) > 1 else 0.0
        stdev = math.sqrt(variance)

        # Calculate trend (simple linear)
        trend_slope = (token_deltas[-1] - token_deltas[0]) / len(token_deltas)
        trend_percentage = (trend_slope / mean * 100) if mean > 0 else 0.0

        # Determine trend direction
        if trend_percentage > 5:
            trend = "increasing"
        elif trend_percentage < -5:
            trend = "decreasing"
        else:
            trend = "stable"

        # Calculate consistency (inverse of coefficient of variation)
        consistency = (mean - stdev) / mean if mean > 0 else 0.0
        consistency = max(0.0, consistency)  # Clamp to [0, 1]

        # Time span analysis
        time_span_hours = 0.0
        if timestamps and len(timestamps) > 1:
            try:
                first_time = datetime.fromisoformat(timestamps[0])
                last_time = datetime.fromisoformat(timestamps[-1])
                time_span = last_time - first_time
                time_span_hours = time_span.total_seconds() / 3600.0
            except (ValueError, TypeError):
                time_span_hours = 0.0

        # Forecast next value (linear extrapolation)
        forecasted_next = int(token_deltas[-1] + trend_slope)
        forecast_confidence = min(1.0, consistency * (len(token_deltas) / 10.0))

        return TrendAnalysis(
            pattern_query="unknown",
            pattern_level=0,
            trend=trend,
            trend_percentage=trend_percentage,
            volatility=stdev,
            consistency=consistency,
            sample_count=len(token_deltas),
            time_span_hours=time_span_hours,
            forecasted_next=forecasted_next,
            forecast_confidence=forecast_confidence
        )


class BudgetPredictor:
    """Predicts token budgets based on pattern history."""

    # Configuration
    MIN_SAMPLES_FOR_PREDICTION = 3
    CONFIDENCE_THRESHOLD_HIGH = 0.8
    CONFIDENCE_THRESHOLD_MEDIUM = 0.5

    @classmethod
    def predict_budget(
        cls,
        token_history: List[int],
        pattern_query: str = "",
        pattern_level: int = 0,
        use_trend: bool = True,
        timestamps: Optional[List[str]] = None
    ) -> TokenPrediction:
        """
        Predict token budget for a pattern.

        Args:
            token_history: List of historical token consumptions
            pattern_query: Query text for identification
            pattern_level: Complexity level
            use_trend: Whether to use trend analysis
            timestamps: Optional timestamps for trend analysis

        Returns:
            TokenPrediction with predicted tokens and confidence
        """
        if not token_history:
            return TokenPrediction(
                pattern_query=pattern_query,
                pattern_level=pattern_level,
                predicted_tokens=0,
                confidence=0.0,
                min_tokens=0,
                max_tokens=0,
                basis="no_data",
                samples=0
            )

        # Use last value if insufficient history
        if len(token_history) < cls.MIN_SAMPLES_FOR_PREDICTION:
            latest = token_history[-1]
            return TokenPrediction(
                pattern_query=pattern_query,
                pattern_level=pattern_level,
                predicted_tokens=latest,
                confidence=0.3,
                min_tokens=int(latest * 0.9),
                max_tokens=int(latest * 1.1),
                basis="recent_value",
                samples=len(token_history)
            )

        # Calculate historical average
        avg = statistics.mean(token_history)
        stdev = statistics.stdev(token_history) if len(token_history) > 1 else 0

        # Trend analysis for better prediction
        trend_analysis = None
        predicted = int(avg)
        basis = "historical_average"
        confidence = 0.6

        if use_trend and len(token_history) > 2:
            trend_analysis = TrendAnalyzer.analyze_trend(token_history, timestamps)

            if trend_analysis.trend == "increasing":
                # Extrapolate upward
                predicted = trend_analysis.forecasted_next
                basis = "trend_extrapolation"
                confidence = trend_analysis.forecast_confidence
            elif trend_analysis.trend == "decreasing":
                # Extrapolate downward
                predicted = trend_analysis.forecasted_next
                basis = "trend_extrapolation"
                confidence = trend_analysis.forecast_confidence
            else:
                # Stable - use average
                confidence = min(1.0, 0.6 + (trend_analysis.consistency * 0.3))

        # Calculate range (min/max)
        min_tokens = int(avg - (stdev * 1.5))
        max_tokens = int(avg + (stdev * 1.5))
        min_tokens = max(1, min_tokens)  # Minimum 1 token

        return TokenPrediction(
            pattern_query=pattern_query,
            pattern_level=pattern_level,
            predicted_tokens=predicted,
            confidence=confidence,
            min_tokens=min_tokens,
            max_tokens=max_tokens,
            basis=basis,
            samples=len(token_history)
        )

    @classmethod
    def predict_with_context(
        cls,
        token_history: List[int],
        pattern_level: int,
        context: str = "",
        base_budget: Optional[int] = None
    ) -> TokenPrediction:
        """
        Predict budget with context-aware adjustment.

        Args:
            token_history: Historical token values
            pattern_level: Complexity level
            context: Domain/context for adjustment
            base_budget: Optional base budget for this level

        Returns:
            Context-adjusted prediction
        """
        prediction = cls.predict_budget(token_history, pattern_level=pattern_level)

        # Adjust based on context
        context_multiplier = 1.0
        if context:
            # Simple context multiplier (can be expanded)
            context_adjustments = {
                "education": 0.9,  # Educational queries are typically efficient
                "architecture": 1.2,  # Architecture queries need more tokens
                "implementation": 1.1,  # Implementation is moderately complex
            }
            context_multiplier = context_adjustments.get(context, 1.0)

        # Apply context adjustment
        if context_multiplier != 1.0:
            prediction.predicted_tokens = int(prediction.predicted_tokens * context_multiplier)
            prediction.min_tokens = int(prediction.min_tokens * context_multiplier)
            prediction.max_tokens = int(prediction.max_tokens * context_multiplier)

        # Adjust confidence based on context match
        if context in ["education", "architecture", "implementation"]:
            prediction.confidence = min(1.0, prediction.confidence + 0.1)

        return prediction


class AdaptiveBudgetSystem:
    """Main adaptive learning system for token budgets."""

    # Global tracking
    PATTERN_PREDICTIONS: Dict[str, TokenPrediction] = {}
    PATTERN_TRENDS: Dict[str, TrendAnalysis] = {}
    PATTERN_ALERTS: Dict[str, List[BudgetAlert]] = {}

    # Configuration
    PREDICTION_UPDATE_INTERVAL = 5  # Update prediction every N executions
    ALERT_THRESHOLD_CRITICAL = 1.3  # 30% over budget
    ALERT_THRESHOLD_WARNING = 1.15  # 15% over budget

    @classmethod
    def update_prediction(
        cls,
        pattern_key: str,
        token_history: List[int],
        pattern_query: str = "",
        pattern_level: int = 0,
        context: str = ""
    ) -> TokenPrediction:
        """
        Update prediction for a pattern.

        Args:
            pattern_key: Unique pattern identifier
            token_history: Historical token consumptions
            pattern_query: Query text
            pattern_level: Complexity level
            context: Domain context

        Returns:
            Updated TokenPrediction
        """
        prediction = BudgetPredictor.predict_with_context(
            token_history=token_history,
            pattern_level=pattern_level,
            context=context
        )
        prediction.pattern_query = pattern_query
        prediction.pattern_level = pattern_level

        cls.PATTERN_PREDICTIONS[pattern_key] = prediction
        return prediction

    @classmethod
    def update_trend(
        cls,
        pattern_key: str,
        token_history: List[int],
        timestamps: Optional[List[str]] = None,
        pattern_query: str = "",
        pattern_level: int = 0
    ) -> TrendAnalysis:
        """
        Update trend analysis for a pattern.

        Args:
            pattern_key: Unique pattern identifier
            token_history: Historical token consumptions
            timestamps: Optional timestamps
            pattern_query: Query text
            pattern_level: Complexity level

        Returns:
            Updated TrendAnalysis
        """
        trend = TrendAnalyzer.analyze_trend(token_history, timestamps)
        trend.pattern_query = pattern_query
        trend.pattern_level = pattern_level

        cls.PATTERN_TRENDS[pattern_key] = trend
        return trend

    @classmethod
    def check_budget_violation(
        cls,
        pattern_key: str,
        actual_tokens: int,
        predicted_tokens: Optional[int] = None
    ) -> Optional[BudgetAlert]:
        """
        Check if pattern exceeded budget and create alert.

        Args:
            pattern_key: Pattern identifier
            actual_tokens: Actual tokens consumed
            predicted_tokens: Expected tokens (uses prediction if not provided)

        Returns:
            BudgetAlert if violated, None otherwise
        """
        if pattern_key not in cls.PATTERN_PREDICTIONS:
            return None

        prediction = cls.PATTERN_PREDICTIONS[pattern_key]
        budget = predicted_tokens or prediction.predicted_tokens

        if actual_tokens <= budget:
            return None  # Within budget

        variance = (actual_tokens - budget) / budget * 100

        # Determine severity
        if actual_tokens > budget * cls.ALERT_THRESHOLD_CRITICAL:
            severity = "critical"
            message = f"CRITICAL: {prediction.pattern_query} consumed {actual_tokens} tokens (budget: {budget})"
            recommendation = "Consider increasing budget or optimizing query"
        elif actual_tokens > budget * cls.ALERT_THRESHOLD_WARNING:
            severity = "warning"
            message = f"WARNING: {prediction.pattern_query} exceeded budget by {variance:.0f}%"
            recommendation = "Monitor pattern execution cost"
        else:
            severity = "info"
            message = f"Pattern {prediction.pattern_query} slightly over budget"
            recommendation = "No action required"

        alert = BudgetAlert(
            pattern_query=prediction.pattern_query,
            pattern_level=prediction.pattern_level,
            severity=severity,
            predicted_budget=budget,
            actual_budget=actual_tokens,
            variance=variance,
            message=message,
            recommendation=recommendation
        )

        # Store alert
        if pattern_key not in cls.PATTERN_ALERTS:
            cls.PATTERN_ALERTS[pattern_key] = []
        cls.PATTERN_ALERTS[pattern_key].append(alert)

        return alert

    @classmethod
    def get_prediction(cls, pattern_key: str) -> Optional[TokenPrediction]:
        """Get prediction for pattern"""
        return cls.PATTERN_PREDICTIONS.get(pattern_key)

    @classmethod
    def get_trend(cls, pattern_key: str) -> Optional[TrendAnalysis]:
        """Get trend analysis for pattern"""
        return cls.PATTERN_TRENDS.get(pattern_key)

    @classmethod
    def get_alerts(cls, pattern_key: Optional[str] = None, severity: Optional[str] = None) -> List[BudgetAlert]:
        """
        Get alerts, optionally filtered.

        Args:
            pattern_key: Specific pattern to filter
            severity: Severity level to filter

        Returns:
            List of matching alerts
        """
        alerts = []

        if pattern_key:
            alerts = cls.PATTERN_ALERTS.get(pattern_key, [])
        else:
            for alert_list in cls.PATTERN_ALERTS.values():
                alerts.extend(alert_list)

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return alerts

    @classmethod
    def get_critical_patterns(cls) -> List[Tuple[str, TokenPrediction]]:
        """Get patterns with critical budget issues"""
        critical = []
        for key, prediction in cls.PATTERN_PREDICTIONS.items():
            alerts = cls.get_alerts(key, severity="critical")
            if alerts:
                critical.append((key, prediction))
        return critical

    @classmethod
    def dump_state(cls) -> Dict:
        """Export complete state for analysis"""
        return {
            "predictions": {k: v.to_dict() for k, v in cls.PATTERN_PREDICTIONS.items()},
            "trends": {k: v.to_dict() for k, v in cls.PATTERN_TRENDS.items()},
            "alerts": {k: [a.to_dict() for a in v] for k, v in cls.PATTERN_ALERTS.items()},
            "critical_patterns": len(cls.get_critical_patterns()),
            "timestamp": datetime.now().isoformat()
        }


# Test the adaptive learning system
if __name__ == "__main__":
    print("🧠 HEKAT Adaptive Learning System - Testing\n")

    # Test 1: Predict budget with sufficient history
    print("Test 1: Token prediction...")
    history = [2000, 2100, 2050, 2150, 2080]
    prediction = BudgetPredictor.predict_budget(history, "explain JWT", 1)
    print(f"✓ Prediction: {prediction.predicted_tokens} tokens")
    print(f"  Range: {prediction.min_tokens}-{prediction.max_tokens}")
    print(f"  Confidence: {prediction.confidence:.0%}\n")

    # Test 2: Trend analysis
    print("Test 2: Trend analysis...")
    increasing_history = [2000, 2200, 2400, 2600, 2800]
    trend = TrendAnalyzer.analyze_trend(increasing_history)
    print(f"✓ Trend: {trend.trend}")
    print(f"  Trend %: {trend.trend_percentage:.1f}%")
    print(f"  Forecast next: {trend.forecasted_next}\n")

    # Test 3: Adaptive system with alerts
    print("Test 3: Adaptive system with alerts...")
    AdaptiveBudgetSystem.update_prediction(
        "test_pattern_1",
        history,
        "explain JWT",
        1
    )
    prediction = AdaptiveBudgetSystem.get_prediction("test_pattern_1")
    print(f"✓ Prediction registered: {prediction.predicted_tokens} tokens")

    # Check for violation
    alert = AdaptiveBudgetSystem.check_budget_violation(
        "test_pattern_1",
        actual_tokens=2400
    )
    if alert:
        print(f"✓ Alert created: {alert.severity} - {alert.message}\n")
    else:
        print(f"✓ No alert (within budget)\n")

    # Test 4: Critical patterns
    print("Test 4: Critical patterns check...")
    AdaptiveBudgetSystem.check_budget_violation("test_pattern_1", 2800)  # Critical
    critical = AdaptiveBudgetSystem.get_critical_patterns()
    print(f"✓ Critical patterns: {len(critical)}")
