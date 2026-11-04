"""Knowledge Representation and Rule-Based Reasoning for ENSO (El Niño & La Niña).

This module defines the explicit Knowledge-Based System (KBS) specification for
the KMRV (Knowledge-driven Model for Representation & Verification) architecture.
It codifies two foundational dimensions of climate intelligence:

1. DESCRIPTIVE (DECLARATIVE) KNOWLEDGE:
   - Ontological concepts, definitions, and domain facts of ENSO.
   - Dataset entity schemas, coordinates, spatial bounding boxes, and variable registries
     spanning NOAA OISST v2.1, CPC ONI, SOI, IOD/DMI, regional SST, rainfall, and MHW stores.
   - Deterministic rule bases: phase detection thresholds, episode persistence requirements
     (NOAA 5-season rule), intensity categories, atmospheric coupling criteria,
     phase-locking seasonality, and compound teleconnections (ENSO x IOD).

2. PROCEDURAL KNOWLEDGE:
   - Causal physical lifecycle: the sequence of natural processes governing ENSO
     (Preconditioning -> Triggering -> Bjerknes Positive Feedback -> Atmospheric Walker
      Reorganization -> Phase-Locking Peak -> Delayed/Recharge Oscillator Decay).
   - Algorithmic data processing procedures: the step-by-step mathematical and
     operational pipeline transforming raw gridded/tabular observations into validated
     ENSO episodes, intensity scores, atmospheric coupling verifications, and regional impact
     evaluations.

References:
    - Trenberth, K. E. (1997). The Definition of El Niño. Bull. Amer. Meteor. Soc., 78, 2771-2777.
    - NOAA Climate Prediction Center (CPC) Operational Definitions for ONI & RONI.
    - Saji, N. H., et al. (1999). A dipole mode in the tropical Indian Ocean. Nature, 401, 360-363.
    - Hobday, A. J., et al. (2016). A hierarchical approach to defining marine heatwaves.
      Progress in Oceanography, 141, 227-238.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ==============================================================================
# SECTION 1: DESCRIPTIVE KNOWLEDGE - TAXONOMIES & ENUMS
# ==============================================================================

class ENSOPhase(str, Enum):
    """Primary ENSO thermal phases."""
    EL_NINO = "El Niño"
    LA_NINA = "La Niña"
    NEUTRAL = "Netral"


class ENSOIntensity(str, Enum):
    """Intensity classifications based on absolute anomaly magnitude."""
    NEUTRAL = "Netral"
    WEAK = "Weak"
    MODERATE = "Moderate"
    STRONG = "Strong"
    VERY_STRONG = "Very Strong"  # Super El Niño / Extreme La Niña


class AtmosphericState(str, Enum):
    """Coupled atmospheric state classification."""
    EL_NINO_COUPLED = "El Niño Coupled (Weakened Walker Circulation, Negative SOI)"
    LA_NINA_COUPLED = "La Niña Coupled (Enhanced Walker Circulation, Positive SOI)"
    NEUTRAL_COUPLED = "Neutral Coupling"
    DECOUPLED = "Decoupled / Transition"


class IODPhase(str, Enum):
    """Indian Ocean Dipole (Dipole Mode Index) phases."""
    POSITIVE_IOD = "Positive IOD"
    NEGATIVE_IOD = "Negative IOD"
    NEUTRAL_IOD = "Neutral IOD"


class CompoundRiskLevel(str, Enum):
    """Compound ocean-atmosphere regional impact risk assessment."""
    EXTREME_DROUGHT = "Extreme Drought & Fire Risk (Indonesia/Maritime Continent)"
    MODERATE_DRY = "Moderate Dryness / Delayed Monsoon"
    NORMAL = "Normal / Climatological Conditions"
    MODERATE_WET = "Moderate Wetness / Enhanced Rainfall"
    EXTREME_FLOOD = "Extreme Flood & Severe Rainfall Risk (Indonesia/Maritime Continent)"


# ==============================================================================
# SECTION 2: DESCRIPTIVE KNOWLEDGE - SPATIAL & DATASET ENTITIES
# ==============================================================================

@dataclass(frozen=True)
class SpatialBoundingBox:
    """Geographic bounding box for climate observation and index calculation."""
    name: str
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float
    description: str

    def contains(self, lat: float, lon: float) -> bool:
        """Check whether a point is within this bounding box."""
        # Normalize longitude to [-180, 180] if necessary
        lon_norm = ((lon + 180.0) % 360.0) - 180.0
        return (self.lat_min <= lat <= self.lat_max) and (self.lon_min <= lon_norm <= self.lon_max)


@dataclass(frozen=True)
class DatasetEntitySpec:
    """Metadata and variable definitions for dataset stores."""
    group_name: str
    storage_type: str  # 'zarr', 'csv', 'sql'
    temporal_resolution: str
    primary_variables: Tuple[str, ...]
    description: str
    role_in_analysis: str


# --- Spatial Entities Registry ---
SPATIAL_ENTITIES: Dict[str, SpatialBoundingBox] = {
    # Equatorial Pacific ENSO Reference Sectors
    "Nino34": SpatialBoundingBox(
        name="Niño 3.4",
        lat_min=-5.0,
        lat_max=5.0,
        lon_min=-170.0,
        lon_max=-120.0,
        description="Official NOAA index sector for Oceanic Niño Index (ONI) and RONI.",
    ),
    "Nino3": SpatialBoundingBox(
        name="Niño 3",
        lat_min=-5.0,
        lat_max=5.0,
        lon_min=-150.0,
        lon_max=-90.0,
        description="Eastern equatorial Pacific warm pool evolution monitor.",
    ),
    "Nino4": SpatialBoundingBox(
        name="Niño 4",
        lat_min=-5.0,
        lat_max=5.0,
        lon_min=160.0,
        lon_max=-150.0,
        description="Central/western Pacific Modoki El Niño diagnostic sector.",
    ),
    "Nino12": SpatialBoundingBox(
        name="Niño 1+2",
        lat_min=-10.0,
        lat_max=0.0,
        lon_min=-90.0,
        lon_max=-80.0,
        description="Coastal South America (Peru/Ecuador) upwelling zone.",
    ),

    # Indonesian Regional Project Domains (Impact Verification)
    "Selat_Makassar": SpatialBoundingBox(
        name="Selat Makassar",
        lat_min=-5.0,
        lat_max=2.0,
        lon_min=116.0,
        lon_max=120.0,
        description="Indonesian Throughflow (ITF) central passage.",
    ),
    "Selat_Karimata": SpatialBoundingBox(
        name="Selat Karimata",
        lat_min=-3.0,
        lat_max=2.0,
        lon_min=105.0,
        lon_max=110.0,
        description="Shallow western Indonesian shelf connecting Java Sea and South China Sea.",
    ),
    "Selatan_Jawa": SpatialBoundingBox(
        name="Selatan Jawa",
        lat_min=-12.0,
        lat_max=-8.0,
        lon_min=105.0,
        lon_max=115.0,
        description="Southern Java eastern Indian Ocean coastal upwelling domain.",
    ),
    "Maluku_Utara_Papua": SpatialBoundingBox(
        name="Maluku Utara - Papua",
        lat_min=-3.0,
        lat_max=3.0,
        lon_min=125.0,
        lon_max=140.0,
        description="Eastern Indonesian Halmahera and Pacific gateway.",
    ),

    # Indian Ocean Dipole (IOD) Poles
    "WTIO": SpatialBoundingBox(
        name="Western Tropical Indian Ocean (WTIO)",
        lat_min=-10.0,
        lat_max=10.0,
        lon_min=50.0,
        lon_max=70.0,
        description="Western pole of the Indian Ocean Dipole.",
    ),
    "SETIO": SpatialBoundingBox(
        name="Southeastern Tropical Indian Ocean (SETIO)",
        lat_min=-10.0,
        lat_max=0.0,
        lon_min=90.0,
        lon_max=110.0,
        description="Eastern pole of the Indian Ocean Dipole off Sumatra-Java.",
    ),
}

# --- Dataset Entities Registry (Zarr, CSV, SQL) ---
DATASET_ENTITIES: Dict[str, DatasetEntitySpec] = {
    "data_oni/oni": DatasetEntitySpec(
        group_name="data_oni/oni",
        storage_type="zarr",
        temporal_resolution="Monthly (centered on 3-month seasonal running means)",
        primary_variables=("ANOM", "TOTAL", "SEAS", "YR", "Month", "Date"),
        description="Official NOAA Climate Prediction Center (CPC) ONI series.",
        role_in_analysis="Ground-truth baseline for ENSO phase classification and episode duration.",
    ),
    "sst_5_wilayah/pasifik_nino34": DatasetEntitySpec(
        group_name="sst_5_wilayah/pasifik_nino34",
        storage_type="zarr",
        temporal_resolution="Daily NOAA OISST v2.1 0.25 deg grid (aggregated monthly in store)",
        primary_variables=("sst", "lat", "lon", "time"),
        description="Gridded sea surface temperature in the equatorial Pacific Niño 3.4 box.",
        role_in_analysis="Source grid for project-derived spatial SSTA and thermal evolution tracking.",
    ),
    "data_soi/soi": DatasetEntitySpec(
        group_name="data_soi/soi",
        storage_type="zarr",
        temporal_resolution="Monthly",
        primary_variables=("SOI",),
        description="Southern Oscillation Index (standardized Tahiti minus Darwin SLP difference).",
        role_in_analysis="Atmospheric counterpart to SST, verifying coupled ocean-atmosphere feedback.",
    ),
    "data_dmi/dmi": DatasetEntitySpec(
        group_name="data_dmi/dmi",
        storage_type="zarr",
        temporal_resolution="Monthly",
        primary_variables=("DMI",),
        description="Dipole Mode Index for the Indian Ocean Dipole (WTIO minus SETIO SSTA).",
        role_in_analysis="Modulating concurrent climate driver for Indonesian rainfall anomalies.",
    ),
    "data_rainfall_monthly/malaysia": DatasetEntitySpec(
        group_name="data_rainfall_monthly/malaysia",
        storage_type="zarr",
        temporal_resolution="Monthly (132 months, 2015-2025)",
        primary_variables=("r1h", "r1h_avg", "r1q", "r3h", "r3h_avg", "rfh", "rfh_avg", "n_obs"),
        description="Subnational Malaysian decadal rainfall aggregated to monthly means.",
        role_in_analysis="Regional equatorial Maritime Continent rainfall response indicator.",
    ),
    "data_rainfall_monthly/hawaii": DatasetEntitySpec(
        group_name="data_rainfall_monthly/hawaii",
        storage_type="zarr",
        temporal_resolution="Monthly (132 months, 2015-2025)",
        primary_variables=("rain_mean_daily_mm", "rain_total_mm", "n_stations"),
        description="Hawaiʻi Climate Data Portal regional daily station averages scaled to monthly totals.",
        role_in_analysis="North-central subtropical Pacific cross-regional teleconnection control.",
    ),
    "data_mhw/mhw_labels": DatasetEntitySpec(
        group_name="data_mhw/mhw_labels",
        storage_type="zarr",
        temporal_resolution="Monthly aggregated MHW metrics (132 months)",
        primary_variables=(
            "Pasifik_Nino34_is_mhw", "Pasifik_Nino34_p90", "Pasifik_Nino34_sst",
            "Selat_Makassar_is_mhw", "Selat_Makassar_p90", "Selat_Makassar_sst",
            "Selat_Karimata_is_mhw", "Selat_Karimata_p90", "Selat_Karimata_sst",
            "Selatan_Jawa_is_mhw", "Selatan_Jawa_p90", "Selatan_Jawa_sst",
            "Maluku_Utara_Papua_is_mhw", "Maluku_Utara_Papua_p90", "Maluku_Utara_Papua_sst",
        ),
        description="Marine Heatwave indicators based on Hobday et al. local 90th percentile threshold.",
        role_in_analysis="Evaluation of regional marine heatwave extremes vs. global ENSO phase.",
    ),
    "postgres_climate_indices": DatasetEntitySpec(
        group_name="public.climate_indices",
        storage_type="sql",
        temporal_resolution="Daily / Monthly Date index",
        primary_variables=("index_id", "date", "enso_index", "iod_index", "created_at"),
        description="PostgreSQL relational repository for synchronized climate indices.",
        role_in_analysis="High-speed structured queries and feature joins for ML models.",
    ),
    "postgres_mhw_predictions": DatasetEntitySpec(
        group_name="public.mhw_predictions",
        storage_type="sql",
        temporal_resolution="Forecast issuance date",
        primary_variables=(
            "prediction_id", "region_name", "target_date", "sst_anomaly",
            "enso_index", "iod_index", "mhw_category", "duration_days", "model_version"
        ),
        description="Output inference predictions from hybrid PyTorch LSTM + LightGBM pipelines.",
        role_in_analysis="Persistent storage of hindcast and operational prediction results.",
    ),
    "postgres_model_metrics": DatasetEntitySpec(
        group_name="public.model_metrics",
        storage_type="sql",
        temporal_resolution="Evaluation run timestamp",
        primary_variables=(
            "metric_id", "model_name", "target_variable", "region_name", "lead_horizon",
            "mae", "rmse", "r2_score", "accuracy", "f1_score", "roc_auc", "brier_score"
        ),
        description="Model performance and forecast evaluation metrics per horizon and target.",
        role_in_analysis="Systematic benchmarking against statistical baselines and model comparison.",
    ),
}

SEASON_CENTER_MONTH: Dict[str, int] = {
    "DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4,
    "AMJ": 5, "MJJ": 6, "JJA": 7, "JAS": 8,
    "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12,
}

MONTH_TO_SEASON_CENTER: Dict[int, str] = {v: k for k, v in SEASON_CENTER_MONTH.items()}


# ==============================================================================
# SECTION 3: DESCRIPTIVE KNOWLEDGE - RULES SPECIFICATIONS
# ==============================================================================

@dataclass(frozen=True)
class ThresholdRule:
    """Declarative specification of numerical threshold rules."""
    name: str
    variable: str
    condition_operator: str
    threshold_value: float
    output_state: str
    description: str


# --- Declarative Rule Registry ---
DECLARATIVE_RULES: Dict[str, Any] = {
    # 1. Thermal Phase Threshold Rules (NOAA Standard)
    "RULE_ENSO_PHASE_THRESHOLD": {
        "index": "ONI (Oceanic Niño Index: 3-month running mean SSTA in Niño 3.4)",
        "unit": "°C",
        "reference_base": "30-year centered climatology (e.g. 1991-2020 base period)",
        "cases": [
            {
                "phase": ENSOPhase.EL_NINO,
                "condition": "ONI >= +0.5",
                "description": "Anomalous sea surface warming in the central-eastern equatorial Pacific.",
            },
            {
                "phase": ENSOPhase.LA_NINA,
                "condition": "ONI <= -0.5",
                "description": "Anomalous sea surface cooling in the central-eastern equatorial Pacific.",
            },
            {
                "phase": ENSOPhase.NEUTRAL,
                "condition": "-0.5 < ONI < +0.5",
                "description": "Near-average equatorial Pacific sea surface temperatures.",
            },
        ],
    },

    # 2. Historical Episode Duration Rule (NOAA CPC Operational Rule)
    "RULE_NOAA_EPISODE_PERSISTENCE": {
        "rule_id": "NOAA_CPC_5_CONSECUTIVE_SEASONS",
        "description": (
            "To qualify as an official El Niño or La Niña episode (event), the ONI threshold "
            "(>= +0.5 °C for El Niño, <= -0.5 °C for La Niña) must be met for a minimum of "
            "five consecutive overlapping 3-month seasons."
        ),
        "min_consecutive_seasons": 5,
        "consequence_of_failure": (
            "Anomalies meeting the threshold for fewer than 5 consecutive seasons are classified "
            "as transient warming/cooling pulses or warm/cool conditions, not full episodes."
        ),
    },

    # 3. Intensity & Severity Classification Rules
    "RULE_ENSO_INTENSITY_LEVELS": {
        "metric": "abs(ONI)",
        "levels": [
            {
                "level": ENSOIntensity.WEAK,
                "min_anomaly": 0.5,
                "max_anomaly": 0.9999,
                "impact": "Mild atmospheric shifts; regional responses easily masked by internal variability.",
            },
            {
                "level": ENSOIntensity.MODERATE,
                "min_anomaly": 1.0,
                "max_anomaly": 1.4999,
                "impact": "Clear shift in tropical convection and identifiable regional precipitation changes.",
            },
            {
                "level": ENSOIntensity.STRONG,
                "min_anomaly": 1.5,
                "max_anomaly": 1.9999,
                "impact": "Widespread teleconnections, substantial disruption of monsoon rains, elevated fire/flood risk.",
            },
            {
                "level": ENSOIntensity.VERY_STRONG,
                "min_anomaly": 2.0,
                "max_anomaly": float("inf"),
                "impact": (
                    "Super El Niño / Extreme episode (e.g. 1982/83, 1997/98, 2015/16). "
                    "Global ecological, meteorological, and economic ramifications."
                ),
            },
        ],
    },

    # 4. Atmospheric Coupling Verification Rules (SOI & Walker Circulation)
    "RULE_ATMOSPHERIC_COUPLING": {
        "metric": "Southern Oscillation Index (SOI: Standardized Tahiti SLP - Darwin SLP)",
        "mechanisms": [
            {
                "phase": ENSOPhase.EL_NINO,
                "soi_expectation": "SOI < 0 (Persistently negative, typically SOI <= -7 in standard index)",
                "trade_winds": "Weakened easterly trade winds or Westerly Wind Bursts (WWBs)",
                "walker_circulation": "Weakened or reversed ascending branch shifted eastward",
                "coupling_state": AtmosphericState.EL_NINO_COUPLED,
            },
            {
                "phase": ENSOPhase.LA_NINA,
                "soi_expectation": "SOI > 0 (Persistently positive, typically SOI >= +7 in standard index)",
                "trade_winds": "Intensified easterly trade winds along the equator",
                "walker_circulation": "Enhanced Walker circulation with vigorous ascending branch over Indonesia",
                "coupling_state": AtmosphericState.LA_NINA_COUPLED,
            },
            {
                "phase": ENSOPhase.NEUTRAL,
                "soi_expectation": "SOI fluctuates near zero (-7 < SOI < +7)",
                "trade_winds": "Climatological easterly trades maintain western warm pool",
                "walker_circulation": "Normal Walker circulation with ascent over Maritime Continent",
                "coupling_state": AtmosphericState.NEUTRAL_COUPLED,
            },
        ],
    },

    # 5. Seasonal Phase-Locking Rules
    "RULE_PHASE_LOCKING_SEASONALITY": {
        "principle": "ENSO tends to synchronize with the annual solar cycle.",
        "seasonal_progression": {
            "Onset_Transition": ["MAM", "AMJ", "JJA"],  # Boreal Spring - Summer (March - August)
            "Growth_Phase": ["JAS", "ASO", "SON"],      # Boreal Autumn (August - November)
            "Peak_Maturity": ["OND", "NDJ", "DJF"],     # Boreal Winter (October - February)
            "Decay_Termination": ["JFM", "FMA", "MAM"], # Boreal Late Winter - Spring (January - May)
        },
        "spring_predictability_barrier": (
            "Forecast skill decreases sharply when predicting through Boreal Spring (March-May) "
            "due to weak ocean-atmosphere coupling and rapid background state transition."
        ),
    },

    # 6. Compound Climate Driver Rules (ENSO x IOD Interaction)
    "RULE_IOD_COMPOUND_TELECONNECTION": {
        "metric": "Dipole Mode Index (DMI = SSTA_WTIO - SSTA_SETIO)",
        "threshold": 0.4,  # standard threshold in deg C
        "combinations": [
            {
                "enso": ENSOPhase.EL_NINO,
                "iod": IODPhase.POSITIVE_IOD,
                "risk": CompoundRiskLevel.EXTREME_DROUGHT,
                "mechanism": (
                    "El Niño (Pacific subsidence) + Positive IOD (cooler eastern Indian Ocean SST) "
                    "mutually suppress convection over Indonesia, causing catastrophic drought & forest fires."
                ),
            },
            {
                "enso": ENSOPhase.EL_NINO,
                "iod": IODPhase.NEGATIVE_IOD,
                "risk": CompoundRiskLevel.MODERATE_DRY,
                "mechanism": (
                    "Warm eastern Indian Ocean SST (Negative IOD) counteracts El Niño dryness, "
                    "mitigating precipitation deficits over western/central Indonesia."
                ),
            },
            {
                "enso": ENSOPhase.LA_NINA,
                "iod": IODPhase.NEGATIVE_IOD,
                "risk": CompoundRiskLevel.EXTREME_FLOOD,
                "mechanism": (
                    "La Niña (enhanced Pacific convergence) + Negative IOD (warm waters off Sumatra-Java) "
                    "synergistically trigger torrential rainfall, flooding, and widespread landslides."
                ),
            },
            {
                "enso": ENSOPhase.LA_NINA,
                "iod": IODPhase.POSITIVE_IOD,
                "risk": CompoundRiskLevel.MODERATE_WET,
                "mechanism": "Positive IOD partially dampens the excess wetness induced by La Niña.",
            },
            {
                "enso": ENSOPhase.NEUTRAL,
                "iod": IODPhase.NEUTRAL_IOD,
                "risk": CompoundRiskLevel.NORMAL,
                "mechanism": "Precipitation driven predominantly by seasonal monsoon transitions and MJO.",
            },
        ],
    },

    # 7. Marine Heatwave (MHW) vs. ENSO Distinction Rules
    "RULE_MHW_VS_ENSO_DISTINCTION": {
        "distinction": (
            "ENSO anomaly thresholds (+/- 0.5 °C in Niño 3.4) DO NOT define Marine Heatwaves (MHW). "
            "A Marine Heatwave requires local daily SST to exceed the 90th percentile of local "
            "seasonal climatology for at least 5 consecutive days (Hobday et al., 2016)."
        ),
        "local_regions": [
            "Selat_Makassar", "Selat_Karimata", "Selatan_Jawa", "Maluku_Utara_Papua", "Pasifik_Nino34"
        ],
    },
}


# ==============================================================================
# SECTION 4: PROCEDURAL KNOWLEDGE - CAUSAL PHYSICAL LIFECYCLE
# ==============================================================================

@dataclass
class PhysicalLifecyclePhase:
    """Represents a discrete stage in the natural ENSO causal chain."""
    step_number: int
    stage_name: str
    primary_medium: str  # 'Oceanic', 'Atmospheric', 'Coupled'
    causal_mechanisms: List[str]
    observable_signatures: List[str]


PHYSICAL_PROCEDURAL_LIFECYCLE: List[PhysicalLifecyclePhase] = [
    PhysicalLifecyclePhase(
        step_number=1,
        stage_name="Preconditioning / Heat Accumulation (Recharge Phase)",
        primary_medium="Oceanic",
        causal_mechanisms=[
            "Persistent easterly trade winds push surface waters westward.",
            "Warm Water Volume (WWV) accumulates in the western Pacific warm pool.",
            "Equatorial thermocline deepens in the west (>150m) and shoals in the east (<50m).",
            "Off-equatorial Sverdrup transport recharges the equatorial heat reservoir.",
        ],
        observable_signatures=[
            "Positive subsurface heat content anomalies in western equatorial Pacific.",
            "Normal or slightly positive SOI.",
            "Niño 3.4 SST anomalies remain neutral or slightly cool.",
        ],
    ),
    PhysicalLifecyclePhase(
        step_number=2,
        stage_name="Triggering / Atmospheric Perturbation",
        primary_medium="Coupled",
        causal_mechanisms=[
            "Intense Madden-Julian Oscillation (MJO) active phase or Westerly Wind Bursts (WWBs).",
            "Abrupt slackening or reversal of low-level equatorial easterlies.",
            "Downwelling equatorial Kelvin waves are generated in the western Pacific.",
            "Kelvin waves propagate eastward along the thermocline toward South America (~2 months transit).",
        ],
        observable_signatures=[
            "Westerly 850 hPa wind anomalies across the western/central Pacific.",
            "Eastward-propagating positive subsurface temperature anomaly pulse.",
            "Thermocline deepens progressively eastward.",
        ],
    ),
    PhysicalLifecyclePhase(
        step_number=3,
        stage_name="Bjerknes Positive Feedback (Coupled Amplification)",
        primary_medium="Coupled",
        causal_mechanisms=[
            "Downwelling Kelvin waves depress the thermocline in the eastern Pacific.",
            "Upwelling of cold subsurface water is reduced off the Galapagos and South America.",
            "Eastern and central Pacific SST warms, increasing local convection.",
            "Zonal SST gradient between western warm pool and eastern cold tongue collapses.",
            "Atmospheric Walker circulation weakens, further collapsing trade winds.",
            "Weakened trades further depress upwelling, creating runaway warming.",
        ],
        observable_signatures=[
            "Niño 3.4 and Niño 3 SSTA exceed +0.5 °C.",
            "SOI falls into negative values.",
            "Convective clouds and anomalous low outgoing longwave radiation (OLR) shift eastward.",
        ],
    ),
    PhysicalLifecyclePhase(
        step_number=4,
        stage_name="Mature Peak / Phase-Locking",
        primary_medium="Coupled",
        causal_mechanisms=[
            "Thermal anomalies attain maximum spatial extent and intensity.",
            "Atmospheric Walker circulation ascending branch centers over the central/eastern Pacific.",
            "Strong descent and subsidence dominate over the Maritime Continent (Indonesia).",
            "Maximum phase locking to the annual cycle occurs during Boreal Winter (Nov-Jan).",
        ],
        observable_signatures=[
            "ONI reaches peak (>= +1.0 °C up to > +2.5 °C for Super El Niño).",
            "SOI persistently negative (<= -7).",
            "Severe rainfall deficit over Indonesia and Malaysia.",
            "Warm pool fully displaced eastward toward the International Date Line.",
        ],
    ),
    PhysicalLifecyclePhase(
        step_number=5,
        stage_name="Termination & Reversal (Delayed & Recharge Oscillator)",
        primary_medium="Oceanic",
        causal_mechanisms=[
            "Delayed Oscillator: Upwelling off-equatorial Rossby waves propagate westward, "
            "reflect at western boundary as upwelling Kelvin waves propagating eastward.",
            "Recharge-Discharge Oscillator: Equatorial warm water volume is discharged "
            "poleward via geostrophic Sverdrup transport, starving the equator of heat.",
            "Thermocline shoals along the equator; trade winds strengthen.",
            "Cold tongue re-emerges in the east, initiating decay or transition to La Niña.",
        ],
        observable_signatures=[
            "Equatorial Warm Water Volume drops below climatology.",
            "Niño 3.4 SSTA drops toward zero during Boreal Spring (March-May).",
            "SOI recovers toward neutral/positive values.",
            "Easterly trade winds re-establish their baseline strength.",
        ],
    ),
]


# ==============================================================================
# SECTION 5: PROCEDURAL KNOWLEDGE - DATA PROCESSING & VERIFICATION PIPELINE
# ==============================================================================

def compute_spatial_mean(
    data: np.ndarray,
    lats: np.ndarray,
    weights_type: str = "cosine",
) -> float:
    """Compute area-weighted spatial mean across latitude and longitude coordinates.

    Procedural rule:
        Grid cell areas decrease towards the poles proportional to cos(latitude).
        Spatial averaging over gridded climate stores must apply cosine-latitude weighting.

    Args:
        data: 2D array of climate observations [lat, lon].
        lats: 1D array of latitude coordinates corresponding to axis 0.
        weights_type: Weighting scheme ('cosine' or 'uniform').

    Returns:
        Weighted scalar mean sea surface temperature.
    """
    if weights_type == "cosine":
        weights = np.cos(np.deg2rad(lats))
        # Broadcast weights to match data shape [lat, lon]
        weights_2d = np.broadcast_to(weights[:, np.newaxis], data.shape)
        valid_mask = ~np.isnan(data)
        if not np.any(valid_mask):
            return float("nan")
        weighted_sum = np.nansum(data * weights_2d)
        total_weights = np.nansum(weights_2d * valid_mask)
        return float(weighted_sum / total_weights)
    else:
        return float(np.nanmean(data))


def compute_climatology(
    series: pd.Series,
    group_by: str = "month",
) -> pd.Series:
    """Compute base period climatology (seasonal cycle).

    Args:
        series: DatetimeIndex-indexed series of values.
        group_by: Grouping key ('month' for monthly, 'dayofyear' for daily).

    Returns:
        Climatological mean per grouping interval.
    """
    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError("Series index must be a pd.DatetimeIndex.")

    if group_by == "month":
        return series.groupby(series.index.month).mean()
    elif group_by == "dayofyear":
        return series.groupby(series.index.dayofyear).mean()
    else:
        raise ValueError(f"Unsupported group_by: {group_by}")


def compute_ssta(
    series: pd.Series,
    climatology: Optional[pd.Series] = None,
    group_by: str = "month",
) -> pd.Series:
    """Compute Sea Surface Temperature Anomaly (SSTA) relative to climatology.

    Formula:
        SSTA(t) = SST(t) - Climatology(month(t))
    """
    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError("Series index must be a pd.DatetimeIndex.")

    if climatology is None:
        climatology = compute_climatology(series, group_by=group_by)

    if group_by == "month":
        clim_mapped = series.index.month.map(climatology)
    elif group_by == "dayofyear":
        clim_mapped = series.index.dayofyear.map(climatology)
    else:
        raise ValueError(f"Unsupported group_by: {group_by}")

    ssta = series - clim_mapped
    ssta.name = f"{series.name or 'sst'}_anom"
    return ssta


def compute_oni(
    ssta_series: pd.Series,
    window: int = 3,
    min_periods: int = 1,
    center: bool = False,
) -> pd.Series:
    """Compute the Oceanic Niño Index (ONI) via 3-month running mean.

    Args:
        ssta_series: Monthly SSTA series in Niño 3.4 region.
        window: Running mean window length (default: 3 months).
        min_periods: Minimum observations required in window.
        center: Whether to center the rolling window.

    Returns:
        Smoothed ONI series.
    """
    oni = ssta_series.rolling(window=window, min_periods=min_periods, center=center).mean()
    oni.name = "ONI"
    return oni


def classify_enso_phase(
    oni_value: float,
    threshold: float = 0.5,
) -> ENSOPhase:
    """Classify a single ONI value into its instantaneous ENSO phase.

    Declarative rule:
        ONI >= +0.5 °C  -> El Niño
        ONI <= -0.5 °C  -> La Niña
        Otherwise       -> Neutral
    """
    if pd.isna(oni_value):
        return ENSOPhase.NEUTRAL
    if oni_value >= threshold:
        return ENSOPhase.EL_NINO
    elif oni_value <= -threshold:
        return ENSOPhase.LA_NINA
    else:
        return ENSOPhase.NEUTRAL


def detect_noaa_episodes(
    oni_series: pd.Series,
    threshold: float = 0.5,
    min_consecutive: int = 5,
) -> pd.DataFrame:
    """Procedural algorithm detecting official NOAA-standard ENSO episodes.

    Rules applied:
        1. Anomaly threshold: ONI >= +0.5 °C (warm) or ONI <= -0.5 °C (cold).
        2. Persistence requirement: qualifying anomaly must persist for at least
           `min_consecutive` consecutive overlapping seasons.
        3. Break tracking: gaps reset episode blocks.

    Args:
        oni_series: Monthly/seasonal ONI series.
        threshold: Absolute anomaly threshold in °C (default: 0.5).
        min_consecutive: Minimum required consecutive seasons (default: 5).

    Returns:
        DataFrame enriched with boolean flags and verified episode status.
    """
    df = pd.DataFrame({"ONI": oni_series})

    # Step 1: Instantaneous threshold masks
    df["warm_qualifying"] = df["ONI"] >= threshold
    df["cold_qualifying"] = df["ONI"] <= -threshold

    # Step 2: Block identification via cumulative sum on phase changes
    df["warm_block"] = (df["warm_qualifying"] != df["warm_qualifying"].shift()).cumsum()
    df["cold_block"] = (df["cold_qualifying"] != df["cold_qualifying"].shift()).cumsum()

    # Step 3: Run-length count within each block
    df["warm_run_length"] = df["warm_qualifying"].groupby(df["warm_block"]).transform("sum")
    df["cold_run_length"] = df["cold_qualifying"].groupby(df["cold_block"]).transform("sum")

    # Step 4: Verification of minimum duration rule (>= 5 seasons)
    df["is_elnino_episode"] = df["warm_qualifying"] & (df["warm_run_length"] >= min_consecutive)
    df["is_lanina_episode"] = df["cold_qualifying"] & (df["cold_run_length"] >= min_consecutive)

    # Step 5: Assign final episode status
    conditions = [
        df["is_elnino_episode"],
        df["is_lanina_episode"],
    ]
    choices = [ENSOPhase.EL_NINO.value, ENSOPhase.LA_NINA.value]
    df["ENSO_Episode"] = np.select(conditions, choices, default=ENSOPhase.NEUTRAL.value)

    # Instantaneous phase (unrestricted by duration) for comparison
    df["ENSO_Instantaneous"] = np.select(
        [df["warm_qualifying"], df["cold_qualifying"]],
        [ENSOPhase.EL_NINO.value, ENSOPhase.LA_NINA.value],
        default=ENSOPhase.NEUTRAL.value,
    )

    return df


def classify_enso_intensity(
    phase: Union[ENSOPhase, str],
    anomaly_value: float,
) -> ENSOIntensity:
    """Classify the intensity category of an ENSO anomaly.

    Rules:
        Weak:        0.5 <= |anomaly| < 1.0 °C
        Moderate:    1.0 <= |anomaly| < 1.5 °C
        Strong:      1.5 <= |anomaly| < 2.0 °C
        Very Strong: |anomaly| >= 2.0 °C
        Neutral:     otherwise
    """
    phase_str = phase.value if isinstance(phase, ENSOPhase) else str(phase)
    if phase_str == ENSOPhase.NEUTRAL.value or pd.isna(anomaly_value):
        return ENSOIntensity.NEUTRAL

    abs_anom = abs(anomaly_value)
    if abs_anom >= 2.0:
        return ENSOIntensity.VERY_STRONG
    elif abs_anom >= 1.5:
        return ENSOIntensity.STRONG
    elif abs_anom >= 1.0:
        return ENSOIntensity.MODERATE
    elif abs_anom >= 0.5:
        return ENSOIntensity.WEAK
    else:
        return ENSOIntensity.NEUTRAL


def verify_atmospheric_coupling(
    enso_phase: Union[ENSOPhase, str],
    soi_value: float,
    soi_threshold: float = 7.0,
) -> AtmosphericState:
    """Procedurally verify coupled ocean-atmosphere interaction using SOI.

    Rule:
        El Niño with SOI <= -threshold -> El Niño Coupled
        La Niña with SOI >= +threshold -> La Niña Coupled
        Neutral phase with normal SOI   -> Neutral Coupled
        Otherwise                       -> Decoupled / Transition
    """
    phase_str = enso_phase.value if isinstance(enso_phase, ENSOPhase) else str(enso_phase)
    if pd.isna(soi_value):
        return AtmosphericState.DECOUPLED

    if phase_str == ENSOPhase.EL_NINO.value and soi_value <= -soi_threshold:
        return AtmosphericState.EL_NINO_COUPLED
    elif phase_str == ENSOPhase.LA_NINA.value and soi_value >= soi_threshold:
        return AtmosphericState.LA_NINA_COUPLED
    elif phase_str == ENSOPhase.NEUTRAL.value and abs(soi_value) < soi_threshold:
        return AtmosphericState.NEUTRAL_COUPLED
    else:
        return AtmosphericState.DECOUPLED


def evaluate_compound_iod_enso(
    enso_phase: Union[ENSOPhase, str],
    dmi_value: float,
    dmi_threshold: float = 0.4,
) -> Tuple[IODPhase, CompoundRiskLevel]:
    """Procedurally evaluate compound IOD-ENSO interaction and regional risk.

    Args:
        enso_phase: Verified ENSO phase.
        dmi_value: Dipole Mode Index value in °C.
        dmi_threshold: Threshold defining active IOD events (default: 0.4 °C).

    Returns:
        Tuple of (IODPhase, CompoundRiskLevel).
    """
    phase_str = enso_phase.value if isinstance(enso_phase, ENSOPhase) else str(enso_phase)

    # Step 1: Determine IOD phase
    if pd.isna(dmi_value):
        iod_phase = IODPhase.NEUTRAL_IOD
    elif dmi_value >= dmi_threshold:
        iod_phase = IODPhase.POSITIVE_IOD
    elif dmi_value <= -dmi_threshold:
        iod_phase = IODPhase.NEGATIVE_IOD
    else:
        iod_phase = IODPhase.NEUTRAL_IOD

    # Step 2: Cross-evaluate compound risk
    if phase_str == ENSOPhase.EL_NINO.value and iod_phase == IODPhase.POSITIVE_IOD:
        risk = CompoundRiskLevel.EXTREME_DROUGHT
    elif phase_str == ENSOPhase.EL_NINO.value and iod_phase == IODPhase.NEGATIVE_IOD:
        risk = CompoundRiskLevel.MODERATE_DRY
    elif phase_str == ENSOPhase.EL_NINO.value:
        risk = CompoundRiskLevel.MODERATE_DRY
    elif phase_str == ENSOPhase.LA_NINA.value and iod_phase == IODPhase.NEGATIVE_IOD:
        risk = CompoundRiskLevel.EXTREME_FLOOD
    elif phase_str == ENSOPhase.LA_NINA.value and iod_phase == IODPhase.POSITIVE_IOD:
        risk = CompoundRiskLevel.MODERATE_WET
    elif phase_str == ENSOPhase.LA_NINA.value:
        risk = CompoundRiskLevel.MODERATE_WET
    elif iod_phase == IODPhase.POSITIVE_IOD:
        risk = CompoundRiskLevel.MODERATE_DRY
    elif iod_phase == IODPhase.NEGATIVE_IOD:
        risk = CompoundRiskLevel.MODERATE_WET
    else:
        risk = CompoundRiskLevel.NORMAL

    return iod_phase, risk


def assess_regional_impacts(
    enso_phase: Union[ENSOPhase, str],
    intensity: Union[ENSOIntensity, str],
    compound_risk: CompoundRiskLevel,
) -> Dict[str, str]:
    """Synthesize descriptive impact assessment across project domains.

    Domains evaluated:
        1. Indonesian Regional Waters (Selat Makassar, Selat Karimata, Selatan Jawa)
        2. Maritime Continent Rainfall (Malaysia)
        3. Subtropical North Pacific Rainfall (Hawaii)
    """
    phase_str = enso_phase.value if isinstance(enso_phase, ENSOPhase) else str(enso_phase)
    intensity_str = intensity.value if isinstance(intensity, ENSOIntensity) else str(intensity)

    if phase_str == ENSOPhase.EL_NINO.value:
        return {
            "Indonesian_Waters": (
                f"Elevated coastal upwelling in Southern Java; depressed SST in central/eastern seas. "
                f"Local Marine Heatwaves suppressed except during late-stage relaxation ({intensity_str})."
            ),
            "Malaysia_Rainfall": (
                f"Anomalous precipitation deficit expected. Convective suppression and delayed monsoon "
                f"onset. Compound risk status: {compound_risk.value}."
            ),
            "Hawaii_Rainfall": (
                "Displaced subtropical jet stream; variable rainfall with elevated winter storm "
                "frequency but reduced trade-wind orographic showers."
            ),
        }
    elif phase_str == ENSOPhase.LA_NINA.value:
        return {
            "Indonesian_Waters": (
                f"Warm water accumulation across Indonesian seas; suppressed coastal upwelling. "
                f"Elevated risk of localized Marine Heatwaves (MHWs) in Selat Makassar & Karimata ({intensity_str})."
            ),
            "Malaysia_Rainfall": (
                f"Enhanced deep atmospheric convection; increased cumulative rainfall totals, "
                f"elevated risk of flash floods and monsoon surges. Compound risk: {compound_risk.value}."
            ),
            "Hawaii_Rainfall": (
                "Strengthened trade wind flow with enhanced orographic precipitation on windward slopes; "
                "reduced leeward Kona storm activity."
            ),
        }
    else:
        return {
            "Indonesian_Waters": "Near-climatological SST and normal seasonal upwelling patterns.",
            "Malaysia_Rainfall": "Rainfall driven primarily by local monsoon cycles and MJO passage.",
            "Hawaii_Rainfall": "Normal seasonal trade-wind precipitation distribution.",
        }


# ==============================================================================
# SECTION 6: END-TO-END EXECUTION PIPELINE
# ==============================================================================

@dataclass
class ClimateEvaluationResult:
    """Structured container holding comprehensive ENSO evaluation outputs."""
    date: pd.Timestamp
    oni_value: float
    instantaneous_phase: ENSOPhase
    episode_phase: ENSOPhase
    intensity: ENSOIntensity
    atmospheric_coupling: AtmosphericState
    iod_phase: IODPhase
    compound_risk: CompoundRiskLevel
    regional_impacts: Dict[str, str]


def evaluate_enso_record(
    date: pd.Timestamp,
    oni_value: float,
    is_episode: bool,
    soi_value: Optional[float] = None,
    dmi_value: Optional[float] = None,
) -> ClimateEvaluationResult:
    """Procedural evaluation orchestrator for a single timepoint record."""
    inst_phase = classify_enso_phase(oni_value)
    ep_phase = inst_phase if is_episode else ENSOPhase.NEUTRAL
    intensity = classify_enso_intensity(ep_phase, oni_value)
    atm_coupling = verify_atmospheric_coupling(ep_phase, soi_value or 0.0)
    iod_phase, risk = evaluate_compound_iod_enso(ep_phase, dmi_value or 0.0)
    impacts = assess_regional_impacts(ep_phase, intensity, risk)

    return ClimateEvaluationResult(
        date=date,
        oni_value=oni_value,
        instantaneous_phase=inst_phase,
        episode_phase=ep_phase,
        intensity=intensity,
        atmospheric_coupling=atm_coupling,
        iod_phase=iod_phase,
        compound_risk=risk,
        regional_impacts=impacts,
    )


def process_climate_dataset(
    df: pd.DataFrame,
    date_col: str = "Date",
    oni_col: str = "ANOM",
    soi_col: Optional[str] = "SOI",
    dmi_col: Optional[str] = "DMI",
) -> pd.DataFrame:
    """Full procedural batch processing across an input climate DataFrame.

    Enriches the dataset with all declarative and procedural knowledge rules:
    - 5-season NOAA episode detection
    - Intensity classification
    - Atmospheric SOI coupling
    - IOD compound risk assessment
    """
    df_out = df.copy()
    if date_col in df_out.columns:
        df_out[date_col] = pd.to_datetime(df_out[date_col])
        df_out = df_out.sort_values(date_col).reset_index(drop=True)

    oni_series = df_out[oni_col]

    # Run episode persistence detection
    episodes_df = detect_noaa_episodes(oni_series, threshold=0.5, min_consecutive=5)
    df_out["ENSO_Phase_Instantaneous"] = episodes_df["ENSO_Instantaneous"]
    df_out["ENSO_Phase_Episode"] = episodes_df["ENSO_Episode"]
    df_out["Is_Episode"] = df_out["ENSO_Phase_Episode"] != ENSOPhase.NEUTRAL.value

    # Evaluate intensity
    df_out["ENSO_Intensity"] = [
        classify_enso_intensity(p, a).value
        for p, a in zip(df_out["ENSO_Phase_Episode"], df_out[oni_col])
    ]

    # Evaluate atmospheric coupling if SOI is present
    if soi_col and soi_col in df_out.columns:
        df_out["Atmospheric_Coupling"] = [
            verify_atmospheric_coupling(p, s).value
            for p, s in zip(df_out["ENSO_Phase_Episode"], df_out[soi_col])
        ]
    else:
        df_out["Atmospheric_Coupling"] = AtmosphericState.NEUTRAL_COUPLED.value

    # Evaluate compound IOD risk if DMI is present
    if dmi_col and dmi_col in df_out.columns:
        iod_results = [
            evaluate_compound_iod_enso(p, d)
            for p, d in zip(df_out["ENSO_Phase_Episode"], df_out[dmi_col])
        ]
        df_out["IOD_Phase"] = [r[0].value for r in iod_results]
        df_out["Compound_Risk"] = [r[1].value for r in iod_results]
    else:
        df_out["IOD_Phase"] = IODPhase.NEUTRAL_IOD.value
        df_out["Compound_Risk"] = CompoundRiskLevel.NORMAL.value

    return df_out


# ==============================================================================
# SECTION 7: MODULE VERIFICATION & DEMONSTRATION
# ==============================================================================

def print_knowledge_summary() -> None:
    """Print structured knowledge summary to console for audit & verification."""
    print("=" * 80)
    print("KMRV CLIMATE INTELLIGENCE KNOWLEDGE BASE: ENSO (EL NIÑO & LA NIÑA)")
    print("=" * 80)
    print("\n[1] SPATIAL ENTITIES (BOUNDING BOXES):")
    for key, box in SPATIAL_ENTITIES.items():
        print(f"  • {box.name} ({key}):")
        print(f"      Lat: [{box.lat_min}°, {box.lat_max}°], Lon: [{box.lon_min}°, {box.lon_max}°]")
        print(f"      Role: {box.description}")

    print("\n[2] DATASET ENTITIES (ZARR / SQL REGISTRIES):")
    for key, spec in DATASET_ENTITIES.items():
        print(f"  • {spec.group_name} ({spec.storage_type.upper()}):")
        print(f"      Temporal: {spec.temporal_resolution}")
        print(f"      Variables: {', '.join(spec.primary_variables[:4])}{'...' if len(spec.primary_variables) > 4 else ''}")
        print(f"      Role: {spec.role_in_analysis}")

    print("\n[3] DECLARATIVE RULES (THRESHOLDS & METRICS):")
    for rule_name, rule_def in DECLARATIVE_RULES.items():
        print(f"  • {rule_name}:")
        if isinstance(rule_def, dict):
            if "description" in rule_def:
                print(f"      {rule_def['description']}")
            elif "distinction" in rule_def:
                print(f"      {rule_def['distinction']}")
            elif "index" in rule_def:
                print(f"      Index: {rule_def['index']}, Unit: {rule_def.get('unit', '')}")
                for c in rule_def.get("cases", []):
                    print(f"        - {c['phase'].value}: {c['condition']} ({c['description']})")
            elif "levels" in rule_def:
                for lvl in rule_def.get("levels", []):
                    print(f"        - {lvl['level'].value}: min={lvl['min_anomaly']}°C, max={lvl['max_anomaly']}°C -> {lvl['impact']}")
            elif "mechanisms" in rule_def:
                for mech in rule_def.get("mechanisms", []):
                    print(f"        - {mech['phase'].value}: SOI expectation={mech['soi_expectation']} -> {mech['coupling_state'].value}")
            elif "combinations" in rule_def:
                for comb in rule_def.get("combinations", []):
                    print(f"        - {comb['enso'].value} + {comb['iod'].value} -> {comb['risk'].value}")
            elif "principle" in rule_def:
                print(f"      Principle: {rule_def['principle']}")

    print("\n[4] PHYSICAL PROCEDURAL LIFECYCLE (NATURAL STAGES):")
    for phase in PHYSICAL_PROCEDURAL_LIFECYCLE:
        print(f"  Stage {phase.step_number}: {phase.stage_name} [{phase.primary_medium}]")
        print(f"    - Mechanisms: {phase.causal_mechanisms[0]}")
        print(f"    - Signature:  {phase.observable_signatures[0]}")

    print("=" * 80)


if __name__ == "__main__":
    print_knowledge_summary()

    # Verification with synthetic historical test series
    print("\n[TEST PIPELINE EXECUTION ON SAMPLE EPISODES]:")
    sample_dates = pd.date_range("2023-01-01", periods=12, freq="MS")
    # Simulated El Niño developing from neutral to strong
    sample_oni = [0.1, 0.3, 0.6, 0.8, 1.1, 1.4, 1.7, 2.1, 2.0, 1.8, 1.2, 0.4]
    sample_soi = [2.0, 0.5, -4.0, -8.5, -11.0, -14.2, -18.0, -22.5, -19.0, -15.0, -9.0, -2.0]
    sample_dmi = [0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 0.8, 0.6, 0.4, 0.2, 0.0, -0.1]

    sample_df = pd.DataFrame({
        "Date": sample_dates,
        "ANOM": sample_oni,
        "SOI": sample_soi,
        "DMI": sample_dmi,
    })

    processed_df = process_climate_dataset(sample_df, oni_col="ANOM", soi_col="SOI", dmi_col="DMI")
    display_cols = [
        "Date", "ANOM", "ENSO_Phase_Instantaneous", "ENSO_Phase_Episode",
        "ENSO_Intensity", "Atmospheric_Coupling", "Compound_Risk"
    ]
    print(processed_df[display_cols].to_string(index=False))
