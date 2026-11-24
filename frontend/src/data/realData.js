// Generated from dataset/features_master_unscaled.csv and model/ artifacts. Do not hand-edit.
export const realData = {
  "meta": {
    "datasetStart": "2016-01",
    "datasetEnd": "2026-03",
    "rows": 123,
    "source": "dataset/features_master_unscaled.csv",
    "bestValidationHorizon": 12,
    "phaseRule": "El Nino > +0,5 C; La Nina < -0,5 C; Netral [-0,5, +0,5]",
    "climatology": "Anomali SST = SST - rata-rata bulan yang sama (2016-2025)"
  },
  "latestSnapshot": {
    "period": "2026-03",
    "date": "2026-03",
    "oni": 0.11,
    "oni_anom": 0.11,
    "soi": 2.0,
    "dmi": 0.285,
    "phase": "Netral",
    "phaseRule": "oni_anom in [-0.5, +0.5]"
  },
  "latest": {
    "period": "2026-03",
    "date": "2026-03",
    "oni": 0.11,
    "oni_anom": 0.11,
    "soi": 2.0,
    "dmi": 0.285,
    "sst": {
      "nino34": 27.206,
      "karimata": 28.396,
      "makassar": 29.221,
      "jawa": 28.719,
      "maluku": 29.211
    },
    "sstAnom": {
      "nino34": -0.202,
      "karimata": -0.31,
      "makassar": -0.155,
      "jawa": -0.516,
      "maluku": -0.226
    },
    "split": "test",
    "phase": "Netral",
    "previousDate": "2026-02",
    "deltaOni": 0.32
  },
  "domainAnomalies": [
    {
      "id": "nino34",
      "label": "Pasifik Ni\u00f1o 3.4",
      "value": -0.202,
      "unit": "\u00b0C"
    },
    {
      "id": "karimata",
      "label": "Selat Karimata",
      "value": -0.31,
      "unit": "\u00b0C"
    },
    {
      "id": "makassar",
      "label": "Selat Makassar",
      "value": -0.155,
      "unit": "\u00b0C"
    },
    {
      "id": "jawa",
      "label": "Selatan Jawa",
      "value": -0.516,
      "unit": "\u00b0C"
    },
    {
      "id": "maluku",
      "label": "Maluku-Papua",
      "value": -0.226,
      "unit": "\u00b0C"
    }
  ],
  "history": [
    {
      "period": "2016-01",
      "date": "2016-01",
      "oni": 2.5,
      "oni_anom": 2.5,
      "soi": -3.6,
      "dmi": 0.265,
      "sst": {
        "nino34": 29.024,
        "karimata": 29.317,
        "makassar": 29.577,
        "jawa": 29.88,
        "maluku": 28.977
      },
      "sstAnom": {
        "nino34": 2.439,
        "karimata": 0.856,
        "makassar": 0.323,
        "jawa": 1.011,
        "maluku": -0.508
      },
      "split": "train"
    },
    {
      "period": "2016-02",
      "date": "2016-02",
      "oni": 2.21,
      "oni_anom": 2.21,
      "soi": -3.2,
      "dmi": -0.11,
      "sst": {
        "nino34": 28.955,
        "karimata": 28.919,
        "makassar": 29.202,
        "jawa": 29.815,
        "maluku": 28.809
      },
      "sstAnom": {
        "nino34": 2.124,
        "karimata": 0.822,
        "makassar": 0.081,
        "jawa": 0.945,
        "maluku": -0.441
      },
      "split": "train"
    },
    {
      "period": "2016-03",
      "date": "2016-03",
      "oni": 1.69,
      "oni_anom": 1.69,
      "soi": -0.1,
      "dmi": -0.008,
      "sst": {
        "nino34": 28.818,
        "karimata": 29.157,
        "makassar": 29.722,
        "jawa": 30.433,
        "maluku": 29.058
      },
      "sstAnom": {
        "nino34": 1.41,
        "karimata": 0.452,
        "makassar": 0.347,
        "jawa": 1.198,
        "maluku": -0.379
      },
      "split": "train"
    },
    {
      "period": "2016-04",
      "date": "2016-04",
      "oni": 1.11,
      "oni_anom": 1.11,
      "soi": -2.0,
      "dmi": 0.146,
      "sst": {
        "nino34": 28.748,
        "karimata": 30.2,
        "makassar": 30.115,
        "jawa": 30.053,
        "maluku": 29.545
      },
      "sstAnom": {
        "nino34": 0.848,
        "karimata": 0.414,
        "makassar": 0.324,
        "jawa": 0.618,
        "maluku": -0.218
      },
      "split": "train"
    },
    {
      "period": "2016-05",
      "date": "2016-05",
      "oni": 0.57,
      "oni_anom": 0.57,
      "soi": 0.7,
      "dmi": -0.113,
      "sst": {
        "nino34": 28.071,
        "karimata": 30.606,
        "makassar": 30.163,
        "jawa": 29.482,
        "maluku": 29.923
      },
      "sstAnom": {
        "nino34": 0.187,
        "karimata": 0.362,
        "makassar": 0.298,
        "jawa": 0.8,
        "maluku": -0.042
      },
      "split": "train"
    },
    {
      "period": "2016-06",
      "date": "2016-06",
      "oni": 0.09,
      "oni_anom": 0.09,
      "soi": 1.1,
      "dmi": -0.443,
      "sst": {
        "nino34": 27.643,
        "karimata": 30.012,
        "makassar": 29.639,
        "jawa": 29.108,
        "maluku": 29.695
      },
      "sstAnom": {
        "nino34": -0.164,
        "karimata": 0.04,
        "makassar": 0.119,
        "jawa": 1.147,
        "maluku": -0.008
      },
      "split": "train"
    },
    {
      "period": "2016-07",
      "date": "2016-07",
      "oni": -0.19,
      "oni_anom": -0.19,
      "soi": 0.7,
      "dmi": -0.757,
      "sst": {
        "nino34": 26.784,
        "karimata": 30.064,
        "makassar": 29.513,
        "jawa": 28.784,
        "maluku": 29.38
      },
      "sstAnom": {
        "nino34": -0.542,
        "karimata": 0.591,
        "makassar": 0.347,
        "jawa": 1.797,
        "maluku": -0.0
      },
      "split": "train"
    },
    {
      "period": "2016-08",
      "date": "2016-08",
      "oni": -0.34,
      "oni_anom": -0.34,
      "soi": 1.2,
      "dmi": -0.443,
      "sst": {
        "nino34": 26.327,
        "karimata": 29.737,
        "makassar": 29.222,
        "jawa": 28.056,
        "maluku": 29.268
      },
      "sstAnom": {
        "nino34": -0.426,
        "karimata": 0.617,
        "makassar": 0.221,
        "jawa": 1.665,
        "maluku": -0.018
      },
      "split": "train"
    },
    {
      "period": "2016-09",
      "date": "2016-09",
      "oni": -0.42,
      "oni_anom": -0.42,
      "soi": 2.0,
      "dmi": -0.437,
      "sst": {
        "nino34": 26.255,
        "karimata": 29.849,
        "makassar": 29.463,
        "jawa": 27.996,
        "maluku": 29.587
      },
      "sstAnom": {
        "nino34": -0.32,
        "karimata": 0.711,
        "makassar": 0.264,
        "jawa": 1.399,
        "maluku": 0.168
      },
      "split": "train"
    },
    {
      "period": "2016-10",
      "date": "2016-10",
      "oni": -0.51,
      "oni_anom": -0.51,
      "soi": -0.4,
      "dmi": -0.371,
      "sst": {
        "nino34": 25.989,
        "karimata": 29.805,
        "makassar": 29.527,
        "jawa": 28.329,
        "maluku": 29.911
      },
      "sstAnom": {
        "nino34": -0.564,
        "karimata": 0.188,
        "makassar": -0.057,
        "jawa": 0.905,
        "maluku": 0.102
      },
      "split": "train"
    },
    {
      "period": "2016-11",
      "date": "2016-11",
      "oni": -0.49,
      "oni_anom": -0.49,
      "soi": -0.2,
      "dmi": -0.382,
      "sst": {
        "nino34": 26.101,
        "karimata": 29.479,
        "makassar": 29.472,
        "jawa": 28.864,
        "maluku": 29.879
      },
      "sstAnom": {
        "nino34": -0.446,
        "karimata": -0.272,
        "makassar": -0.301,
        "jawa": 0.508,
        "maluku": -0.123
      },
      "split": "train"
    },
    {
      "period": "2016-12",
      "date": "2016-12",
      "oni": -0.37,
      "oni_anom": -0.37,
      "soi": 0.5,
      "dmi": -0.31,
      "sst": {
        "nino34": 26.231,
        "karimata": 29.129,
        "makassar": 29.316,
        "jawa": 28.761,
        "maluku": 29.773
      },
      "sstAnom": {
        "nino34": -0.148,
        "karimata": 0.058,
        "makassar": -0.227,
        "jawa": 0.148,
        "maluku": -0.091
      },
      "split": "train"
    },
    {
      "period": "2017-01",
      "date": "2017-01",
      "oni": -0.08,
      "oni_anom": -0.08,
      "soi": 0.3,
      "dmi": -0.086,
      "sst": {
        "nino34": 26.22,
        "karimata": 28.831,
        "makassar": 28.978,
        "jawa": 28.593,
        "maluku": 29.378
      },
      "sstAnom": {
        "nino34": -0.365,
        "karimata": 0.37,
        "makassar": -0.276,
        "jawa": -0.276,
        "maluku": -0.108
      },
      "split": "train"
    },
    {
      "period": "2017-02",
      "date": "2017-02",
      "oni": 0.08,
      "oni_anom": 0.08,
      "soi": -0.1,
      "dmi": 0.101,
      "sst": {
        "nino34": 26.768,
        "karimata": 28.132,
        "makassar": 28.793,
        "jawa": 28.854,
        "maluku": 29.043
      },
      "sstAnom": {
        "nino34": -0.063,
        "karimata": 0.035,
        "makassar": -0.329,
        "jawa": -0.016,
        "maluku": -0.207
      },
      "split": "train"
    },
    {
      "period": "2017-03",
      "date": "2017-03",
      "oni": 0.27,
      "oni_anom": 0.27,
      "soi": 1.5,
      "dmi": 0.357,
      "sst": {
        "nino34": 27.371,
        "karimata": 28.688,
        "makassar": 29.196,
        "jawa": 29.08,
        "maluku": 29.241
      },
      "sstAnom": {
        "nino34": -0.037,
        "karimata": -0.017,
        "makassar": -0.179,
        "jawa": -0.155,
        "maluku": -0.195
      },
      "split": "train"
    },
    {
      "period": "2017-04",
      "date": "2017-04",
      "oni": 0.32,
      "oni_anom": 0.32,
      "soi": -0.3,
      "dmi": 0.498,
      "sst": {
        "nino34": 28.113,
        "karimata": 29.454,
        "makassar": 29.519,
        "jawa": 29.037,
        "maluku": 29.661
      },
      "sstAnom": {
        "nino34": 0.214,
        "karimata": -0.332,
        "makassar": -0.272,
        "jawa": -0.397,
        "maluku": -0.102
      },
      "split": "train"
    },
    {
      "period": "2017-05",
      "date": "2017-05",
      "oni": 0.35,
      "oni_anom": 0.35,
      "soi": 0.4,
      "dmi": 0.536,
      "sst": {
        "nino34": 28.254,
        "karimata": 29.775,
        "makassar": 29.609,
        "jawa": 28.306,
        "maluku": 29.948
      },
      "sstAnom": {
        "nino34": 0.369,
        "karimata": -0.47,
        "makassar": -0.255,
        "jawa": -0.376,
        "maluku": -0.018
      },
      "split": "train"
    },
    {
      "period": "2017-06",
      "date": "2017-06",
      "oni": 0.32,
      "oni_anom": 0.32,
      "soi": -0.7,
      "dmi": 0.424,
      "sst": {
        "nino34": 28.056,
        "karimata": 29.608,
        "makassar": 29.287,
        "jawa": 27.466,
        "maluku": 29.621
      },
      "sstAnom": {
        "nino34": 0.249,
        "karimata": -0.364,
        "makassar": -0.234,
        "jawa": -0.495,
        "maluku": -0.081
      },
      "split": "train"
    },
    {
      "period": "2017-07",
      "date": "2017-07",
      "oni": 0.14,
      "oni_anom": 0.14,
      "soi": 1.3,
      "dmi": 0.52,
      "sst": {
        "nino34": 27.531,
        "karimata": 29.221,
        "makassar": 28.975,
        "jawa": 26.309,
        "maluku": 29.342
      },
      "sstAnom": {
        "nino34": 0.205,
        "karimata": -0.252,
        "makassar": -0.192,
        "jawa": -0.678,
        "maluku": -0.038
      },
      "split": "train"
    },
    {
      "period": "2017-08",
      "date": "2017-08",
      "oni": -0.07,
      "oni_anom": -0.07,
      "soi": 0.9,
      "dmi": 0.349,
      "sst": {
        "nino34": 26.779,
        "karimata": 28.804,
        "makassar": 28.817,
        "jawa": 25.767,
        "maluku": 29.16
      },
      "sstAnom": {
        "nino34": 0.026,
        "karimata": -0.316,
        "makassar": -0.184,
        "jawa": -0.624,
        "maluku": -0.126
      },
      "split": "train"
    },
    {
      "period": "2017-09",
      "date": "2017-09",
      "oni": -0.23,
      "oni_anom": -0.23,
      "soi": 1.0,
      "dmi": 0.035,
      "sst": {
        "nino34": 26.381,
        "karimata": 29.016,
        "makassar": 29.198,
        "jawa": 26.152,
        "maluku": 29.326
      },
      "sstAnom": {
        "nino34": -0.195,
        "karimata": -0.122,
        "makassar": -0.002,
        "jawa": -0.444,
        "maluku": -0.093
      },
      "split": "train"
    },
    {
      "period": "2017-10",
      "date": "2017-10",
      "oni": -0.44,
      "oni_anom": -0.44,
      "soi": 1.5,
      "dmi": 0.015,
      "sst": {
        "nino34": 26.327,
        "karimata": 29.539,
        "makassar": 29.31,
        "jawa": 26.777,
        "maluku": 29.807
      },
      "sstAnom": {
        "nino34": -0.227,
        "karimata": -0.079,
        "makassar": -0.274,
        "jawa": -0.646,
        "maluku": -0.003
      },
      "split": "train"
    },
    {
      "period": "2017-11",
      "date": "2017-11",
      "oni": -0.61,
      "oni_anom": -0.61,
      "soi": 1.5,
      "dmi": 0.289,
      "sst": {
        "nino34": 25.823,
        "karimata": 29.475,
        "makassar": 29.572,
        "jawa": 28.327,
        "maluku": 29.97
      },
      "sstAnom": {
        "nino34": -0.724,
        "karimata": -0.276,
        "makassar": -0.201,
        "jawa": -0.03,
        "maluku": -0.032
      },
      "split": "train"
    },
    {
      "period": "2017-12",
      "date": "2017-12",
      "oni": -0.76,
      "oni_anom": -0.76,
      "soi": -0.2,
      "dmi": 0.11,
      "sst": {
        "nino34": 25.627,
        "karimata": 28.448,
        "makassar": 29.28,
        "jawa": 28.103,
        "maluku": 29.836
      },
      "sstAnom": {
        "nino34": -0.753,
        "karimata": -0.624,
        "makassar": -0.264,
        "jawa": -0.51,
        "maluku": -0.028
      },
      "split": "train"
    },
    {
      "period": "2018-01",
      "date": "2018-01",
      "oni": -0.71,
      "oni_anom": -0.71,
      "soi": 1.8,
      "dmi": -0.2,
      "sst": {
        "nino34": 25.781,
        "karimata": 28.044,
        "makassar": 28.87,
        "jawa": 28.498,
        "maluku": 29.472
      },
      "sstAnom": {
        "nino34": -0.804,
        "karimata": -0.417,
        "makassar": -0.384,
        "jawa": -0.371,
        "maluku": -0.013
      },
      "split": "train"
    },
    {
      "period": "2018-02",
      "date": "2018-02",
      "oni": -0.67,
      "oni_anom": -0.67,
      "soi": -0.8,
      "dmi": 0.216,
      "sst": {
        "nino34": 25.979,
        "karimata": 27.7,
        "makassar": 29.104,
        "jawa": 28.44,
        "maluku": 29.234
      },
      "sstAnom": {
        "nino34": -0.852,
        "karimata": -0.397,
        "makassar": -0.017,
        "jawa": -0.43,
        "maluku": -0.016
      },
      "split": "train"
    },
    {
      "period": "2018-03",
      "date": "2018-03",
      "oni": -0.55,
      "oni_anom": -0.55,
      "soi": 2.4,
      "dmi": -0.12,
      "sst": {
        "nino34": 26.426,
        "karimata": 28.704,
        "makassar": 29.27,
        "jawa": 29.304,
        "maluku": 29.348
      },
      "sstAnom": {
        "nino34": -0.982,
        "karimata": -0.002,
        "makassar": -0.106,
        "jawa": 0.069,
        "maluku": -0.089
      },
      "split": "train"
    },
    {
      "period": "2018-04",
      "date": "2018-04",
      "oni": -0.35,
      "oni_anom": -0.35,
      "soi": 0.8,
      "dmi": -0.083,
      "sst": {
        "nino34": 27.261,
        "karimata": 29.523,
        "makassar": 29.623,
        "jawa": 29.804,
        "maluku": 29.566
      },
      "sstAnom": {
        "nino34": -0.639,
        "karimata": -0.263,
        "makassar": -0.168,
        "jawa": 0.37,
        "maluku": -0.196
      },
      "split": "train"
    },
    {
      "period": "2018-05",
      "date": "2018-05",
      "oni": -0.07,
      "oni_anom": -0.07,
      "soi": 0.6,
      "dmi": 0.122,
      "sst": {
        "nino34": 27.738,
        "karimata": 29.769,
        "makassar": 29.462,
        "jawa": 28.328,
        "maluku": 29.664
      },
      "sstAnom": {
        "nino34": -0.147,
        "karimata": -0.475,
        "makassar": -0.403,
        "jawa": -0.354,
        "maluku": -0.302
      },
      "split": "train"
    },
    {
      "period": "2018-06",
      "date": "2018-06",
      "oni": 0.13,
      "oni_anom": 0.13,
      "soi": -0.2,
      "dmi": 0.155,
      "sst": {
        "nino34": 27.844,
        "karimata": 29.636,
        "makassar": 29.139,
        "jawa": 27.136,
        "maluku": 29.376
      },
      "sstAnom": {
        "nino34": 0.037,
        "karimata": -0.336,
        "makassar": -0.382,
        "jawa": -0.825,
        "maluku": -0.326
      },
      "split": "train"
    },
    {
      "period": "2018-07",
      "date": "2018-07",
      "oni": 0.2,
      "oni_anom": 0.2,
      "soi": 0.4,
      "dmi": 0.053,
      "sst": {
        "nino34": 27.492,
        "karimata": 28.762,
        "makassar": 28.806,
        "jawa": 25.639,
        "maluku": 29.185
      },
      "sstAnom": {
        "nino34": 0.166,
        "karimata": -0.711,
        "makassar": -0.361,
        "jawa": -1.348,
        "maluku": -0.195
      },
      "split": "train"
    },
    {
      "period": "2018-08",
      "date": "2018-08",
      "oni": 0.3,
      "oni_anom": 0.3,
      "soi": -0.5,
      "dmi": 0.121,
      "sst": {
        "nino34": 27.144,
        "karimata": 28.682,
        "makassar": 28.665,
        "jawa": 25.442,
        "maluku": 29.109
      },
      "sstAnom": {
        "nino34": 0.391,
        "karimata": -0.438,
        "makassar": -0.336,
        "jawa": -0.949,
        "maluku": -0.178
      },
      "split": "train"
    },
    {
      "period": "2018-09",
      "date": "2018-09",
      "oni": 0.52,
      "oni_anom": 0.52,
      "soi": -1.5,
      "dmi": 0.604,
      "sst": {
        "nino34": 27.054,
        "karimata": 28.633,
        "makassar": 28.642,
        "jawa": 25.627,
        "maluku": 29.015
      },
      "sstAnom": {
        "nino34": 0.478,
        "karimata": -0.504,
        "makassar": -0.557,
        "jawa": -0.97,
        "maluku": -0.404
      },
      "split": "train"
    },
    {
      "period": "2018-10",
      "date": "2018-10",
      "oni": 0.82,
      "oni_anom": 0.82,
      "soi": 0.6,
      "dmi": 0.684,
      "sst": {
        "nino34": 27.607,
        "karimata": 29.315,
        "makassar": 29.324,
        "jawa": 26.757,
        "maluku": 29.422
      },
      "sstAnom": {
        "nino34": 1.054,
        "karimata": -0.303,
        "makassar": -0.26,
        "jawa": -0.666,
        "maluku": -0.388
      },
      "split": "train"
    },
    {
      "period": "2018-11",
      "date": "2018-11",
      "oni": 1.04,
      "oni_anom": 1.04,
      "soi": -0.1,
      "dmi": 0.5,
      "sst": {
        "nino34": 27.654,
        "karimata": 29.694,
        "makassar": 29.42,
        "jawa": 27.904,
        "maluku": 29.562
      },
      "sstAnom": {
        "nino34": 1.108,
        "karimata": -0.058,
        "makassar": -0.353,
        "jawa": -0.452,
        "maluku": -0.441
      },
      "split": "train"
    },
    {
      "period": "2018-12",
      "date": "2018-12",
      "oni": 1.05,
      "oni_anom": 1.05,
      "soi": 1.7,
      "dmi": 0.309,
      "sst": {
        "nino34": 27.507,
        "karimata": 29.248,
        "makassar": 29.222,
        "jawa": 28.228,
        "maluku": 29.514
      },
      "sstAnom": {
        "nino34": 1.128,
        "karimata": 0.177,
        "makassar": -0.321,
        "jawa": -0.386,
        "maluku": -0.35
      },
      "split": "train"
    },
    {
      "period": "2019-01",
      "date": "2019-01",
      "oni": 0.99,
      "oni_anom": 0.99,
      "soi": -0.1,
      "dmi": 0.387,
      "sst": {
        "nino34": 27.187,
        "karimata": 28.937,
        "makassar": 29.176,
        "jawa": 28.712,
        "maluku": 29.003
      },
      "sstAnom": {
        "nino34": 0.602,
        "karimata": 0.476,
        "makassar": -0.078,
        "jawa": -0.157,
        "maluku": -0.483
      },
      "split": "train"
    },
    {
      "period": "2019-02",
      "date": "2019-02",
      "oni": 0.94,
      "oni_anom": 0.94,
      "soi": -2.3,
      "dmi": 0.416,
      "sst": {
        "nino34": 27.394,
        "karimata": 28.476,
        "makassar": 28.804,
        "jawa": 28.656,
        "maluku": 28.517
      },
      "sstAnom": {
        "nino34": 0.563,
        "karimata": 0.379,
        "makassar": -0.317,
        "jawa": -0.215,
        "maluku": -0.733
      },
      "split": "train"
    },
    {
      "period": "2019-03",
      "date": "2019-03",
      "oni": 0.87,
      "oni_anom": 0.87,
      "soi": -0.5,
      "dmi": 0.225,
      "sst": {
        "nino34": 28.186,
        "karimata": 29.167,
        "makassar": 28.872,
        "jawa": 29.065,
        "maluku": 28.795
      },
      "sstAnom": {
        "nino34": 0.778,
        "karimata": 0.461,
        "makassar": -0.504,
        "jawa": -0.17,
        "maluku": -0.642
      },
      "split": "train"
    },
    {
      "period": "2019-04",
      "date": "2019-04",
      "oni": 0.82,
      "oni_anom": 0.82,
      "soi": 0.2,
      "dmi": 0.258,
      "sst": {
        "nino34": 28.506,
        "karimata": 29.688,
        "makassar": 29.299,
        "jawa": 29.136,
        "maluku": 29.299
      },
      "sstAnom": {
        "nino34": 0.606,
        "karimata": -0.098,
        "makassar": -0.492,
        "jawa": -0.299,
        "maluku": -0.464
      },
      "split": "train"
    },
    {
      "period": "2019-05",
      "date": "2019-05",
      "oni": 0.71,
      "oni_anom": 0.71,
      "soi": -0.7,
      "dmi": 0.54,
      "sst": {
        "nino34": 28.605,
        "karimata": 30.173,
        "makassar": 29.443,
        "jawa": 28.137,
        "maluku": 29.574
      },
      "sstAnom": {
        "nino34": 0.72,
        "karimata": -0.071,
        "makassar": -0.422,
        "jawa": -0.545,
        "maluku": -0.391
      },
      "split": "train"
    },
    {
      "period": "2019-06",
      "date": "2019-06",
      "oni": 0.59,
      "oni_anom": 0.59,
      "soi": -0.7,
      "dmi": 0.605,
      "sst": {
        "nino34": 28.284,
        "karimata": 29.596,
        "makassar": 29.084,
        "jawa": 26.589,
        "maluku": 29.369
      },
      "sstAnom": {
        "nino34": 0.477,
        "karimata": -0.376,
        "makassar": -0.437,
        "jawa": -1.372,
        "maluku": -0.334
      },
      "split": "train"
    },
    {
      "period": "2019-07",
      "date": "2019-07",
      "oni": 0.38,
      "oni_anom": 0.38,
      "soi": -0.6,
      "dmi": 0.597,
      "sst": {
        "nino34": 27.688,
        "karimata": 29.021,
        "makassar": 28.61,
        "jawa": 25.619,
        "maluku": 28.686
      },
      "sstAnom": {
        "nino34": 0.362,
        "karimata": -0.452,
        "makassar": -0.556,
        "jawa": -1.368,
        "maluku": -0.694
      },
      "split": "train"
    },
    {
      "period": "2019-08",
      "date": "2019-08",
      "oni": 0.2,
      "oni_anom": 0.2,
      "soi": -0.2,
      "dmi": 0.436,
      "sst": {
        "nino34": 27.004,
        "karimata": 28.384,
        "makassar": 28.274,
        "jawa": 25.179,
        "maluku": 28.587
      },
      "sstAnom": {
        "nino34": 0.251,
        "karimata": -0.736,
        "makassar": -0.727,
        "jawa": -1.212,
        "maluku": -0.699
      },
      "split": "train"
    },
    {
      "period": "2019-09",
      "date": "2019-09",
      "oni": 0.31,
      "oni_anom": 0.31,
      "soi": -1.9,
      "dmi": 0.892,
      "sst": {
        "nino34": 26.698,
        "karimata": 28.382,
        "makassar": 28.574,
        "jawa": 25.587,
        "maluku": 28.684
      },
      "sstAnom": {
        "nino34": 0.122,
        "karimata": -0.756,
        "makassar": -0.626,
        "jawa": -1.009,
        "maluku": -0.734
      },
      "split": "train"
    },
    {
      "period": "2019-10",
      "date": "2019-10",
      "oni": 0.51,
      "oni_anom": 0.51,
      "soi": -0.6,
      "dmi": 0.964,
      "sst": {
        "nino34": 27.252,
        "karimata": 29.396,
        "makassar": 29.476,
        "jawa": 26.758,
        "maluku": 29.426
      },
      "sstAnom": {
        "nino34": 0.699,
        "karimata": -0.222,
        "makassar": -0.109,
        "jawa": -0.665,
        "maluku": -0.383
      },
      "split": "train"
    },
    {
      "period": "2019-11",
      "date": "2019-11",
      "oni": 0.72,
      "oni_anom": 0.72,
      "soi": -1.4,
      "dmi": 0.835,
      "sst": {
        "nino34": 27.236,
        "karimata": 29.965,
        "makassar": 29.723,
        "jawa": 27.725,
        "maluku": 29.667
      },
      "sstAnom": {
        "nino34": 0.69,
        "karimata": 0.214,
        "makassar": -0.051,
        "jawa": -0.632,
        "maluku": -0.336
      },
      "split": "train"
    },
    {
      "period": "2019-12",
      "date": "2019-12",
      "oni": 0.75,
      "oni_anom": 0.75,
      "soi": -0.9,
      "dmi": 0.243,
      "sst": {
        "nino34": 27.017,
        "karimata": 28.919,
        "makassar": 29.719,
        "jawa": 29.301,
        "maluku": 29.757
      },
      "sstAnom": {
        "nino34": 0.638,
        "karimata": -0.152,
        "makassar": 0.175,
        "jawa": 0.688,
        "maluku": -0.108
      },
      "split": "train"
    },
    {
      "period": "2020-01",
      "date": "2020-01",
      "oni": 0.71,
      "oni_anom": 0.71,
      "soi": 0.3,
      "dmi": 0.173,
      "sst": {
        "nino34": 27.031,
        "karimata": 28.18,
        "makassar": 29.279,
        "jawa": 29.32,
        "maluku": 29.365
      },
      "sstAnom": {
        "nino34": 0.446,
        "karimata": -0.281,
        "makassar": 0.025,
        "jawa": 0.45,
        "maluku": -0.12
      },
      "split": "train"
    },
    {
      "period": "2020-02",
      "date": "2020-02",
      "oni": 0.66,
      "oni_anom": 0.66,
      "soi": -0.1,
      "dmi": 0.054,
      "sst": {
        "nino34": 27.028,
        "karimata": 28.329,
        "makassar": 29.106,
        "jawa": 29.656,
        "maluku": 29.216
      },
      "sstAnom": {
        "nino34": 0.196,
        "karimata": 0.232,
        "makassar": -0.015,
        "jawa": 0.786,
        "maluku": -0.034
      },
      "split": "train"
    },
    {
      "period": "2020-03",
      "date": "2020-03",
      "oni": 0.57,
      "oni_anom": 0.57,
      "soi": -0.2,
      "dmi": 0.019,
      "sst": {
        "nino34": 27.666,
        "karimata": 29.043,
        "makassar": 29.397,
        "jawa": 29.557,
        "maluku": 29.499
      },
      "sstAnom": {
        "nino34": 0.258,
        "karimata": 0.337,
        "makassar": 0.021,
        "jawa": 0.321,
        "maluku": 0.062
      },
      "split": "train"
    },
    {
      "period": "2020-04",
      "date": "2020-04",
      "oni": 0.33,
      "oni_anom": 0.33,
      "soi": 0.3,
      "dmi": -0.011,
      "sst": {
        "nino34": 28.188,
        "karimata": 29.952,
        "makassar": 29.799,
        "jawa": 29.78,
        "maluku": 29.88
      },
      "sstAnom": {
        "nino34": 0.289,
        "karimata": 0.166,
        "makassar": 0.008,
        "jawa": 0.345,
        "maluku": 0.117
      },
      "split": "train"
    },
    {
      "period": "2020-05",
      "date": "2020-05",
      "oni": 0.04,
      "oni_anom": 0.04,
      "soi": 0.7,
      "dmi": 0.298,
      "sst": {
        "nino34": 27.609,
        "karimata": 30.263,
        "makassar": 29.929,
        "jawa": 28.868,
        "maluku": 30.125
      },
      "sstAnom": {
        "nino34": -0.276,
        "karimata": 0.019,
        "makassar": 0.064,
        "jawa": 0.186,
        "maluku": 0.16
      },
      "split": "train"
    },
    {
      "period": "2020-06",
      "date": "2020-06",
      "oni": -0.18,
      "oni_anom": -0.18,
      "soi": -0.6,
      "dmi": 0.455,
      "sst": {
        "nino34": 27.386,
        "karimata": 30.002,
        "makassar": 29.583,
        "jawa": 28.078,
        "maluku": 29.944
      },
      "sstAnom": {
        "nino34": -0.421,
        "karimata": 0.029,
        "makassar": 0.062,
        "jawa": 0.117,
        "maluku": 0.242
      },
      "split": "train"
    },
    {
      "period": "2020-07",
      "date": "2020-07",
      "oni": -0.29,
      "oni_anom": -0.29,
      "soi": 0.7,
      "dmi": 0.319,
      "sst": {
        "nino34": 27.106,
        "karimata": 29.523,
        "makassar": 29.285,
        "jawa": 27.143,
        "maluku": 29.742
      },
      "sstAnom": {
        "nino34": -0.221,
        "karimata": 0.049,
        "makassar": 0.119,
        "jawa": 0.156,
        "maluku": 0.362
      },
      "split": "train"
    },
    {
      "period": "2020-08",
      "date": "2020-08",
      "oni": -0.43,
      "oni_anom": -0.43,
      "soi": 1.8,
      "dmi": -0.183,
      "sst": {
        "nino34": 26.307,
        "karimata": 29.546,
        "makassar": 29.291,
        "jawa": 26.619,
        "maluku": 29.613
      },
      "sstAnom": {
        "nino34": -0.446,
        "karimata": 0.426,
        "makassar": 0.29,
        "jawa": 0.228,
        "maluku": 0.327
      },
      "split": "train"
    },
    {
      "period": "2020-09",
      "date": "2020-09",
      "oni": -0.77,
      "oni_anom": -0.77,
      "soi": 1.5,
      "dmi": -0.189,
      "sst": {
        "nino34": 26.053,
        "karimata": 29.167,
        "makassar": 29.274,
        "jawa": 26.686,
        "maluku": 29.723
      },
      "sstAnom": {
        "nino34": -0.522,
        "karimata": 0.029,
        "makassar": 0.074,
        "jawa": 0.09,
        "maluku": 0.304
      },
      "split": "train"
    },
    {
      "period": "2020-10",
      "date": "2020-10",
      "oni": -1.0,
      "oni_anom": -1.0,
      "soi": 0.8,
      "dmi": 0.074,
      "sst": {
        "nino34": 25.562,
        "karimata": 29.392,
        "makassar": 29.678,
        "jawa": 27.139,
        "maluku": 30.136
      },
      "sstAnom": {
        "nino34": -0.991,
        "karimata": -0.226,
        "makassar": 0.094,
        "jawa": -0.284,
        "maluku": 0.326
      },
      "split": "train"
    },
    {
      "period": "2020-11",
      "date": "2020-11",
      "oni": -1.11,
      "oni_anom": -1.11,
      "soi": 1.1,
      "dmi": 0.02,
      "sst": {
        "nino34": 25.52,
        "karimata": 29.367,
        "makassar": 29.706,
        "jawa": 28.445,
        "maluku": 30.258
      },
      "sstAnom": {
        "nino34": -1.027,
        "karimata": -0.384,
        "makassar": -0.068,
        "jawa": 0.089,
        "maluku": 0.256
      },
      "split": "train"
    },
    {
      "period": "2020-12",
      "date": "2020-12",
      "oni": -1.06,
      "oni_anom": -1.06,
      "soi": 3.0,
      "dmi": 0.031,
      "sst": {
        "nino34": 25.583,
        "karimata": 28.751,
        "makassar": 29.386,
        "jawa": 28.724,
        "maluku": 30.11
      },
      "sstAnom": {
        "nino34": -0.796,
        "karimata": -0.32,
        "makassar": -0.158,
        "jawa": 0.111,
        "maluku": 0.245
      },
      "split": "train"
    },
    {
      "period": "2021-01",
      "date": "2021-01",
      "oni": -0.99,
      "oni_anom": -0.99,
      "soi": 3.2,
      "dmi": 0.051,
      "sst": {
        "nino34": 25.59,
        "karimata": 27.67,
        "makassar": 28.864,
        "jawa": 28.471,
        "maluku": 29.972
      },
      "sstAnom": {
        "nino34": -0.995,
        "karimata": -0.791,
        "makassar": -0.391,
        "jawa": -0.398,
        "maluku": 0.487
      },
      "split": "train"
    },
    {
      "period": "2021-02",
      "date": "2021-02",
      "oni": -0.85,
      "oni_anom": -0.85,
      "soi": 2.5,
      "dmi": 0.243,
      "sst": {
        "nino34": 25.796,
        "karimata": 27.261,
        "makassar": 29.172,
        "jawa": 28.517,
        "maluku": 29.818
      },
      "sstAnom": {
        "nino34": -1.036,
        "karimata": -0.836,
        "makassar": 0.051,
        "jawa": -0.353,
        "maluku": 0.568
      },
      "split": "train"
    },
    {
      "period": "2021-03",
      "date": "2021-03",
      "oni": -0.74,
      "oni_anom": -0.74,
      "soi": 0.6,
      "dmi": 0.267,
      "sst": {
        "nino34": 26.625,
        "karimata": 28.423,
        "makassar": 29.48,
        "jawa": 28.928,
        "maluku": 29.79
      },
      "sstAnom": {
        "nino34": -0.783,
        "karimata": -0.282,
        "makassar": 0.105,
        "jawa": -0.307,
        "maluku": 0.353
      },
      "split": "train"
    },
    {
      "period": "2021-04",
      "date": "2021-04",
      "oni": -0.56,
      "oni_anom": -0.56,
      "soi": 0.6,
      "dmi": 0.25,
      "sst": {
        "nino34": 27.192,
        "karimata": 29.722,
        "makassar": 29.823,
        "jawa": 29.034,
        "maluku": 29.807
      },
      "sstAnom": {
        "nino34": -0.708,
        "karimata": -0.063,
        "makassar": 0.032,
        "jawa": -0.4,
        "maluku": 0.044
      },
      "split": "train"
    },
    {
      "period": "2021-05",
      "date": "2021-05",
      "oni": -0.4,
      "oni_anom": -0.4,
      "soi": 0.8,
      "dmi": 0.009,
      "sst": {
        "nino34": 27.529,
        "karimata": 30.3,
        "makassar": 29.861,
        "jawa": 28.656,
        "maluku": 29.816
      },
      "sstAnom": {
        "nino34": -0.355,
        "karimata": 0.055,
        "makassar": -0.004,
        "jawa": -0.026,
        "maluku": -0.149
      },
      "split": "train"
    },
    {
      "period": "2021-06",
      "date": "2021-06",
      "oni": -0.31,
      "oni_anom": -0.31,
      "soi": 0.7,
      "dmi": -0.002,
      "sst": {
        "nino34": 27.648,
        "karimata": 30.135,
        "makassar": 29.643,
        "jawa": 28.294,
        "maluku": 29.51
      },
      "sstAnom": {
        "nino34": -0.159,
        "karimata": 0.163,
        "makassar": 0.122,
        "jawa": 0.333,
        "maluku": -0.192
      },
      "split": "train"
    },
    {
      "period": "2021-07",
      "date": "2021-07",
      "oni": -0.35,
      "oni_anom": -0.35,
      "soi": 2.3,
      "dmi": -0.229,
      "sst": {
        "nino34": 27.068,
        "karimata": 29.502,
        "makassar": 29.158,
        "jawa": 27.592,
        "maluku": 29.392
      },
      "sstAnom": {
        "nino34": -0.258,
        "karimata": 0.029,
        "makassar": -0.009,
        "jawa": 0.605,
        "maluku": 0.012
      },
      "split": "train"
    },
    {
      "period": "2021-08",
      "date": "2021-08",
      "oni": -0.46,
      "oni_anom": -0.46,
      "soi": 1.0,
      "dmi": -0.099,
      "sst": {
        "nino34": 26.567,
        "karimata": 29.179,
        "makassar": 29.163,
        "jawa": 26.643,
        "maluku": 29.554
      },
      "sstAnom": {
        "nino34": -0.186,
        "karimata": 0.059,
        "makassar": 0.162,
        "jawa": 0.252,
        "maluku": 0.268
      },
      "split": "train"
    },
    {
      "period": "2021-09",
      "date": "2021-09",
      "oni": -0.64,
      "oni_anom": -0.64,
      "soi": 1.3,
      "dmi": -0.058,
      "sst": {
        "nino34": 26.445,
        "karimata": 29.314,
        "makassar": 29.438,
        "jawa": 26.763,
        "maluku": 29.721
      },
      "sstAnom": {
        "nino34": -0.131,
        "karimata": 0.176,
        "makassar": 0.238,
        "jawa": 0.167,
        "maluku": 0.302
      },
      "split": "train"
    },
    {
      "period": "2021-10",
      "date": "2021-10",
      "oni": -0.77,
      "oni_anom": -0.77,
      "soi": 1.2,
      "dmi": -0.091,
      "sst": {
        "nino34": 25.928,
        "karimata": 29.71,
        "makassar": 29.671,
        "jawa": 27.423,
        "maluku": 30.054
      },
      "sstAnom": {
        "nino34": -0.625,
        "karimata": 0.092,
        "makassar": 0.087,
        "jawa": -0.0,
        "maluku": 0.244
      },
      "split": "train"
    },
    {
      "period": "2021-11",
      "date": "2021-11",
      "oni": -0.91,
      "oni_anom": -0.91,
      "soi": 1.6,
      "dmi": 0.069,
      "sst": {
        "nino34": 25.902,
        "karimata": 29.718,
        "makassar": 30.005,
        "jawa": 28.351,
        "maluku": 30.301
      },
      "sstAnom": {
        "nino34": -0.645,
        "karimata": -0.033,
        "makassar": 0.232,
        "jawa": -0.005,
        "maluku": 0.299
      },
      "split": "train"
    },
    {
      "period": "2021-12",
      "date": "2021-12",
      "oni": -0.83,
      "oni_anom": -0.83,
      "soi": 2.5,
      "dmi": -0.12,
      "sst": {
        "nino34": 25.527,
        "karimata": 29.202,
        "makassar": 29.653,
        "jawa": 28.793,
        "maluku": 29.872
      },
      "sstAnom": {
        "nino34": -0.852,
        "karimata": 0.131,
        "makassar": 0.109,
        "jawa": 0.179,
        "maluku": 0.008
      },
      "split": "train"
    },
    {
      "period": "2022-01",
      "date": "2022-01",
      "oni": -0.76,
      "oni_anom": -0.76,
      "soi": 0.8,
      "dmi": -0.056,
      "sst": {
        "nino34": 25.666,
        "karimata": 28.495,
        "makassar": 29.203,
        "jawa": 29.04,
        "maluku": 29.419
      },
      "sstAnom": {
        "nino34": -0.919,
        "karimata": 0.034,
        "makassar": -0.051,
        "jawa": 0.171,
        "maluku": -0.067
      },
      "split": "val"
    },
    {
      "period": "2022-02",
      "date": "2022-02",
      "oni": -0.68,
      "oni_anom": -0.68,
      "soi": 1.8,
      "dmi": -0.082,
      "sst": {
        "nino34": 25.958,
        "karimata": 28.276,
        "makassar": 29.069,
        "jawa": 28.805,
        "maluku": 29.305
      },
      "sstAnom": {
        "nino34": -0.873,
        "karimata": 0.18,
        "makassar": -0.052,
        "jawa": -0.065,
        "maluku": 0.055
      },
      "split": "val"
    },
    {
      "period": "2022-03",
      "date": "2022-03",
      "oni": -0.77,
      "oni_anom": -0.77,
      "soi": 2.9,
      "dmi": -0.093,
      "sst": {
        "nino34": 26.3,
        "karimata": 29.073,
        "makassar": 29.608,
        "jawa": 29.202,
        "maluku": 29.687
      },
      "sstAnom": {
        "nino34": -1.108,
        "karimata": 0.367,
        "makassar": 0.232,
        "jawa": -0.033,
        "maluku": 0.25
      },
      "split": "val"
    },
    {
      "period": "2022-04",
      "date": "2022-04",
      "oni": -0.86,
      "oni_anom": -0.86,
      "soi": 2.8,
      "dmi": -0.068,
      "sst": {
        "nino34": 26.798,
        "karimata": 30.173,
        "makassar": 30.078,
        "jawa": 29.518,
        "maluku": 29.765
      },
      "sstAnom": {
        "nino34": -1.101,
        "karimata": 0.387,
        "makassar": 0.286,
        "jawa": 0.084,
        "maluku": 0.002
      },
      "split": "val"
    },
    {
      "period": "2022-05",
      "date": "2022-05",
      "oni": -0.83,
      "oni_anom": -0.83,
      "soi": 2.4,
      "dmi": -0.122,
      "sst": {
        "nino34": 26.792,
        "karimata": 30.514,
        "makassar": 30.019,
        "jawa": 29.572,
        "maluku": 30.06
      },
      "sstAnom": {
        "nino34": -1.092,
        "karimata": 0.269,
        "makassar": 0.154,
        "jawa": 0.89,
        "maluku": 0.094
      },
      "split": "val"
    },
    {
      "period": "2022-06",
      "date": "2022-06",
      "oni": -0.73,
      "oni_anom": -0.73,
      "soi": 2.8,
      "dmi": -0.335,
      "sst": {
        "nino34": 27.021,
        "karimata": 30.205,
        "makassar": 29.773,
        "jawa": 28.971,
        "maluku": 30.033
      },
      "sstAnom": {
        "nino34": -0.786,
        "karimata": 0.232,
        "makassar": 0.252,
        "jawa": 1.01,
        "maluku": 0.331
      },
      "split": "val"
    },
    {
      "period": "2022-07",
      "date": "2022-07",
      "oni": -0.7,
      "oni_anom": -0.7,
      "soi": 1.3,
      "dmi": -0.195,
      "sst": {
        "nino34": 26.628,
        "karimata": 29.751,
        "makassar": 29.497,
        "jawa": 27.656,
        "maluku": 29.553
      },
      "sstAnom": {
        "nino34": -0.698,
        "karimata": 0.278,
        "makassar": 0.331,
        "jawa": 0.669,
        "maluku": 0.173
      },
      "split": "val"
    },
    {
      "period": "2022-08",
      "date": "2022-08",
      "oni": -0.78,
      "oni_anom": -0.78,
      "soi": 1.7,
      "dmi": -0.246,
      "sst": {
        "nino34": 25.883,
        "karimata": 29.397,
        "makassar": 29.355,
        "jawa": 26.975,
        "maluku": 29.555
      },
      "sstAnom": {
        "nino34": -0.87,
        "karimata": 0.277,
        "makassar": 0.353,
        "jawa": 0.584,
        "maluku": 0.269
      },
      "split": "val"
    },
    {
      "period": "2022-09",
      "date": "2022-09",
      "oni": -0.87,
      "oni_anom": -0.87,
      "soi": 2.7,
      "dmi": -0.322,
      "sst": {
        "nino34": 25.787,
        "karimata": 29.277,
        "makassar": 29.608,
        "jawa": 27.24,
        "maluku": 29.855
      },
      "sstAnom": {
        "nino34": -0.789,
        "karimata": 0.139,
        "makassar": 0.408,
        "jawa": 0.644,
        "maluku": 0.436
      },
      "split": "val"
    },
    {
      "period": "2022-10",
      "date": "2022-10",
      "oni": -0.89,
      "oni_anom": -0.89,
      "soi": 2.8,
      "dmi": -0.691,
      "sst": {
        "nino34": 25.882,
        "karimata": 29.442,
        "makassar": 29.524,
        "jawa": 27.658,
        "maluku": 29.939
      },
      "sstAnom": {
        "nino34": -0.672,
        "karimata": -0.176,
        "makassar": -0.06,
        "jawa": 0.234,
        "maluku": 0.13
      },
      "split": "val"
    },
    {
      "period": "2022-11",
      "date": "2022-11",
      "oni": -0.82,
      "oni_anom": -0.82,
      "soi": 0.5,
      "dmi": -0.269,
      "sst": {
        "nino34": 25.828,
        "karimata": 29.3,
        "makassar": 29.798,
        "jawa": 27.941,
        "maluku": 30.238
      },
      "sstAnom": {
        "nino34": -0.719,
        "karimata": -0.451,
        "makassar": 0.025,
        "jawa": -0.415,
        "maluku": 0.236
      },
      "split": "val"
    },
    {
      "period": "2022-12",
      "date": "2022-12",
      "oni": -0.7,
      "oni_anom": -0.7,
      "soi": 3.5,
      "dmi": -0.091,
      "sst": {
        "nino34": 25.748,
        "karimata": 28.834,
        "makassar": 29.727,
        "jawa": 28.334,
        "maluku": 29.967
      },
      "sstAnom": {
        "nino34": -0.632,
        "karimata": -0.238,
        "makassar": 0.184,
        "jawa": -0.279,
        "maluku": 0.103
      },
      "split": "val"
    },
    {
      "period": "2023-01",
      "date": "2023-01",
      "oni": -0.55,
      "oni_anom": -0.55,
      "soi": 2.3,
      "dmi": 0.11,
      "sst": {
        "nino34": 25.822,
        "karimata": 28.127,
        "makassar": 29.343,
        "jawa": 28.619,
        "maluku": 29.58
      },
      "sstAnom": {
        "nino34": -0.763,
        "karimata": -0.334,
        "makassar": 0.089,
        "jawa": -0.25,
        "maluku": 0.094
      },
      "split": "val"
    },
    {
      "period": "2023-02",
      "date": "2023-02",
      "oni": -0.33,
      "oni_anom": -0.33,
      "soi": 2.3,
      "dmi": 0.157,
      "sst": {
        "nino34": 26.219,
        "karimata": 27.837,
        "makassar": 28.937,
        "jawa": 28.186,
        "maluku": 29.382
      },
      "sstAnom": {
        "nino34": -0.613,
        "karimata": -0.26,
        "makassar": -0.184,
        "jawa": -0.684,
        "maluku": 0.132
      },
      "split": "val"
    },
    {
      "period": "2023-03",
      "date": "2023-03",
      "oni": -0.11,
      "oni_anom": -0.11,
      "soi": 0.3,
      "dmi": 0.414,
      "sst": {
        "nino34": 27.168,
        "karimata": 27.87,
        "makassar": 29.437,
        "jawa": 28.851,
        "maluku": 29.715
      },
      "sstAnom": {
        "nino34": -0.24,
        "karimata": -0.836,
        "makassar": 0.062,
        "jawa": -0.384,
        "maluku": 0.279
      },
      "split": "val"
    },
    {
      "period": "2023-04",
      "date": "2023-04",
      "oni": 0.19,
      "oni_anom": 0.19,
      "soi": 0.4,
      "dmi": 0.56,
      "sst": {
        "nino34": 27.955,
        "karimata": 29.309,
        "makassar": 29.904,
        "jawa": 29.147,
        "maluku": 30.072
      },
      "sstAnom": {
        "nino34": 0.055,
        "karimata": -0.476,
        "makassar": 0.113,
        "jawa": -0.287,
        "maluku": 0.31
      },
      "split": "val"
    },
    {
      "period": "2023-05",
      "date": "2023-05",
      "oni": 0.46,
      "oni_anom": 0.46,
      "soi": -1.7,
      "dmi": 0.443,
      "sst": {
        "nino34": 28.322,
        "karimata": 30.121,
        "makassar": 29.968,
        "jawa": 28.513,
        "maluku": 30.035
      },
      "sstAnom": {
        "nino34": 0.437,
        "karimata": -0.124,
        "makassar": 0.103,
        "jawa": -0.169,
        "maluku": 0.069
      },
      "split": "val"
    },
    {
      "period": "2023-06",
      "date": "2023-06",
      "oni": 0.73,
      "oni_anom": 0.73,
      "soi": 0.4,
      "dmi": 0.665,
      "sst": {
        "nino34": 28.599,
        "karimata": 29.85,
        "makassar": 29.684,
        "jawa": 27.583,
        "maluku": 29.759
      },
      "sstAnom": {
        "nino34": 0.792,
        "karimata": -0.122,
        "makassar": 0.163,
        "jawa": -0.378,
        "maluku": 0.057
      },
      "split": "val"
    },
    {
      "period": "2023-07",
      "date": "2023-07",
      "oni": 1.0,
      "oni_anom": 1.0,
      "soi": -0.4,
      "dmi": 0.498,
      "sst": {
        "nino34": 28.336,
        "karimata": 29.444,
        "makassar": 29.244,
        "jawa": 26.623,
        "maluku": 29.392
      },
      "sstAnom": {
        "nino34": 1.01,
        "karimata": -0.03,
        "makassar": 0.077,
        "jawa": -0.364,
        "maluku": 0.012
      },
      "split": "val"
    },
    {
      "period": "2023-08",
      "date": "2023-08",
      "oni": 1.25,
      "oni_anom": 1.25,
      "soi": -1.4,
      "dmi": 0.826,
      "sst": {
        "nino34": 28.186,
        "karimata": 29.043,
        "makassar": 29.099,
        "jawa": 26.11,
        "maluku": 29.203
      },
      "sstAnom": {
        "nino34": 1.433,
        "karimata": -0.078,
        "makassar": 0.098,
        "jawa": -0.28,
        "maluku": -0.083
      },
      "split": "val"
    },
    {
      "period": "2023-09",
      "date": "2023-09",
      "oni": 1.5,
      "oni_anom": 1.5,
      "soi": -2.1,
      "dmi": 0.946,
      "sst": {
        "nino34": 28.3,
        "karimata": 29.047,
        "makassar": 29.133,
        "jawa": 26.075,
        "maluku": 29.162
      },
      "sstAnom": {
        "nino34": 1.725,
        "karimata": -0.091,
        "makassar": -0.067,
        "jawa": -0.521,
        "maluku": -0.257
      },
      "split": "val"
    },
    {
      "period": "2023-10",
      "date": "2023-10",
      "oni": 1.74,
      "oni_anom": 1.74,
      "soi": -0.8,
      "dmi": 0.804,
      "sst": {
        "nino34": 28.333,
        "karimata": 29.84,
        "makassar": 29.777,
        "jawa": 27.398,
        "maluku": 29.455
      },
      "sstAnom": {
        "nino34": 1.78,
        "karimata": 0.223,
        "makassar": 0.193,
        "jawa": -0.026,
        "maluku": -0.354
      },
      "split": "val"
    },
    {
      "period": "2023-11",
      "date": "2023-11",
      "oni": 1.9,
      "oni_anom": 1.9,
      "soi": -1.3,
      "dmi": 0.92,
      "sst": {
        "nino34": 28.683,
        "karimata": 30.592,
        "makassar": 30.29,
        "jawa": 28.352,
        "maluku": 29.898
      },
      "sstAnom": {
        "nino34": 2.136,
        "karimata": 0.841,
        "makassar": 0.517,
        "jawa": -0.005,
        "maluku": -0.105
      },
      "split": "val"
    },
    {
      "period": "2023-12",
      "date": "2023-12",
      "oni": 1.99,
      "oni_anom": 1.99,
      "soi": -0.4,
      "dmi": 0.852,
      "sst": {
        "nino34": 28.624,
        "karimata": 29.759,
        "makassar": 29.828,
        "jawa": 28.35,
        "maluku": 29.88
      },
      "sstAnom": {
        "nino34": 2.245,
        "karimata": 0.687,
        "makassar": 0.285,
        "jawa": -0.263,
        "maluku": 0.016
      },
      "split": "val"
    },
    {
      "period": "2024-01",
      "date": "2024-01",
      "oni": 1.84,
      "oni_anom": 1.84,
      "soi": 0.8,
      "dmi": 0.765,
      "sst": {
        "nino34": 28.431,
        "karimata": 29.195,
        "makassar": 29.884,
        "jawa": 29.095,
        "maluku": 29.543
      },
      "sstAnom": {
        "nino34": 1.846,
        "karimata": 0.735,
        "makassar": 0.63,
        "jawa": 0.225,
        "maluku": 0.057
      },
      "split": "test"
    },
    {
      "period": "2024-02",
      "date": "2024-02",
      "oni": 1.53,
      "oni_anom": 1.53,
      "soi": -2.3,
      "dmi": 0.327,
      "sst": {
        "nino34": 28.23,
        "karimata": 28.564,
        "makassar": 29.403,
        "jawa": 29.564,
        "maluku": 29.12
      },
      "sstAnom": {
        "nino34": 1.398,
        "karimata": 0.467,
        "makassar": 0.282,
        "jawa": 0.694,
        "maluku": -0.13
      },
      "split": "test"
    },
    {
      "period": "2024-03",
      "date": "2024-03",
      "oni": 1.18,
      "oni_anom": 1.18,
      "soi": 0.6,
      "dmi": 0.421,
      "sst": {
        "nino34": 28.412,
        "karimata": 28.895,
        "makassar": 29.249,
        "jawa": 29.133,
        "maluku": 29.407
      },
      "sstAnom": {
        "nino34": 1.004,
        "karimata": 0.189,
        "makassar": -0.126,
        "jawa": -0.102,
        "maluku": -0.03
      },
      "split": "test"
    },
    {
      "period": "2024-04",
      "date": "2024-04",
      "oni": 0.77,
      "oni_anom": 0.77,
      "soi": -0.3,
      "dmi": 0.44,
      "sst": {
        "nino34": 28.604,
        "karimata": 30.491,
        "makassar": 29.787,
        "jawa": 29.425,
        "maluku": 30.107
      },
      "sstAnom": {
        "nino34": 0.705,
        "karimata": 0.705,
        "makassar": -0.004,
        "jawa": -0.01,
        "maluku": 0.344
      },
      "split": "test"
    },
    {
      "period": "2024-05",
      "date": "2024-05",
      "oni": 0.43,
      "oni_anom": 0.43,
      "soi": 0.8,
      "dmi": 0.298,
      "sst": {
        "nino34": 28.124,
        "karimata": 30.535,
        "makassar": 29.995,
        "jawa": 28.147,
        "maluku": 30.34
      },
      "sstAnom": {
        "nino34": 0.239,
        "karimata": 0.291,
        "makassar": 0.13,
        "jawa": -0.535,
        "maluku": 0.375
      },
      "split": "test"
    },
    {
      "period": "2024-06",
      "date": "2024-06",
      "oni": 0.18,
      "oni_anom": 0.18,
      "soi": 0.1,
      "dmi": 0.197,
      "sst": {
        "nino34": 27.901,
        "karimata": 30.581,
        "makassar": 29.673,
        "jawa": 28.162,
        "maluku": 29.942
      },
      "sstAnom": {
        "nino34": 0.094,
        "karimata": 0.608,
        "makassar": 0.152,
        "jawa": 0.201,
        "maluku": 0.24
      },
      "split": "test"
    },
    {
      "period": "2024-07",
      "date": "2024-07",
      "oni": 0.06,
      "oni_anom": 0.06,
      "soi": -1.2,
      "dmi": 0.033,
      "sst": {
        "nino34": 27.438,
        "karimata": 29.902,
        "makassar": 29.367,
        "jawa": 27.485,
        "maluku": 29.552
      },
      "sstAnom": {
        "nino34": 0.111,
        "karimata": 0.429,
        "makassar": 0.201,
        "jawa": 0.498,
        "maluku": 0.172
      },
      "split": "test"
    },
    {
      "period": "2024-08",
      "date": "2024-08",
      "oni": -0.04,
      "oni_anom": -0.04,
      "soi": 1.5,
      "dmi": 0.267,
      "sst": {
        "nino34": 26.794,
        "karimata": 29.219,
        "makassar": 29.174,
        "jawa": 26.491,
        "maluku": 29.449
      },
      "sstAnom": {
        "nino34": 0.041,
        "karimata": 0.099,
        "makassar": 0.173,
        "jawa": 0.1,
        "maluku": 0.163
      },
      "split": "test"
    },
    {
      "period": "2024-09",
      "date": "2024-09",
      "oni": -0.12,
      "oni_anom": -0.12,
      "soi": -0.2,
      "dmi": 0.115,
      "sst": {
        "nino34": 26.47,
        "karimata": 29.421,
        "makassar": 29.372,
        "jawa": 26.957,
        "maluku": 29.604
      },
      "sstAnom": {
        "nino34": -0.105,
        "karimata": 0.283,
        "makassar": 0.173,
        "jawa": 0.361,
        "maluku": 0.186
      },
      "split": "test"
    },
    {
      "period": "2024-10",
      "date": "2024-10",
      "oni": -0.19,
      "oni_anom": -0.19,
      "soi": 0.8,
      "dmi": -0.196,
      "sst": {
        "nino34": 26.403,
        "karimata": 30.087,
        "makassar": 29.711,
        "jawa": 28.084,
        "maluku": 29.992
      },
      "sstAnom": {
        "nino34": -0.15,
        "karimata": 0.47,
        "makassar": 0.127,
        "jawa": 0.661,
        "maluku": 0.183
      },
      "split": "test"
    },
    {
      "period": "2024-11",
      "date": "2024-11",
      "oni": -0.29,
      "oni_anom": -0.29,
      "soi": 0.8,
      "dmi": -0.382,
      "sst": {
        "nino34": 26.664,
        "karimata": 30.355,
        "makassar": 30.108,
        "jawa": 29.3,
        "maluku": 30.385
      },
      "sstAnom": {
        "nino34": 0.117,
        "karimata": 0.604,
        "makassar": 0.334,
        "jawa": 0.944,
        "maluku": 0.383
      },
      "split": "test"
    },
    {
      "period": "2024-12",
      "date": "2024-12",
      "oni": -0.43,
      "oni_anom": -0.43,
      "soi": 1.9,
      "dmi": -0.331,
      "sst": {
        "nino34": 25.971,
        "karimata": 29.429,
        "makassar": 29.776,
        "jawa": 28.875,
        "maluku": 30.124
      },
      "sstAnom": {
        "nino34": -0.408,
        "karimata": 0.358,
        "makassar": 0.232,
        "jawa": 0.262,
        "maluku": 0.259
      },
      "split": "test"
    },
    {
      "period": "2025-01",
      "date": "2025-01",
      "oni": -0.46,
      "oni_anom": -0.46,
      "soi": 0.3,
      "dmi": -0.196,
      "sst": {
        "nino34": 25.747,
        "karimata": 28.379,
        "makassar": 29.372,
        "jawa": 28.834,
        "maluku": 30.063
      },
      "sstAnom": {
        "nino34": -0.838,
        "karimata": -0.082,
        "makassar": 0.118,
        "jawa": -0.035,
        "maluku": 0.578
      },
      "split": "test"
    },
    {
      "period": "2025-02",
      "date": "2025-02",
      "oni": -0.22,
      "oni_anom": -0.22,
      "soi": 0.9,
      "dmi": 0.017,
      "sst": {
        "nino34": 26.325,
        "karimata": 27.922,
        "makassar": 29.48,
        "jawa": 28.836,
        "maluku": 29.795
      },
      "sstAnom": {
        "nino34": -0.506,
        "karimata": -0.174,
        "makassar": 0.359,
        "jawa": -0.034,
        "maluku": 0.545
      },
      "split": "test"
    },
    {
      "period": "2025-03",
      "date": "2025-03",
      "oni": -0.08,
      "oni_anom": -0.08,
      "soi": 2.8,
      "dmi": 0.058,
      "sst": {
        "nino34": 27.31,
        "karimata": 28.349,
        "makassar": 29.679,
        "jawa": 29.314,
        "maluku": 30.054
      },
      "sstAnom": {
        "nino34": -0.098,
        "karimata": -0.357,
        "makassar": 0.303,
        "jawa": 0.079,
        "maluku": 0.617
      },
      "split": "test"
    },
    {
      "period": "2025-04",
      "date": "2025-04",
      "oni": 0.02,
      "oni_anom": 0.02,
      "soi": 0.9,
      "dmi": 0.149,
      "sst": {
        "nino34": 27.631,
        "karimata": 29.345,
        "makassar": 29.965,
        "jawa": 29.41,
        "maluku": 29.925
      },
      "sstAnom": {
        "nino34": -0.269,
        "karimata": -0.44,
        "makassar": 0.174,
        "jawa": -0.024,
        "maluku": 0.162
      },
      "split": "test"
    },
    {
      "period": "2025-05",
      "date": "2025-05",
      "oni": -0.04,
      "oni_anom": -0.04,
      "soi": 0.7,
      "dmi": 0.107,
      "sst": {
        "nino34": 27.804,
        "karimata": 30.389,
        "makassar": 30.199,
        "jawa": 28.81,
        "maluku": 30.171
      },
      "sstAnom": {
        "nino34": -0.081,
        "karimata": 0.144,
        "makassar": 0.334,
        "jawa": 0.128,
        "maluku": 0.205
      },
      "split": "test"
    },
    {
      "period": "2025-06",
      "date": "2025-06",
      "oni": -0.02,
      "oni_anom": -0.02,
      "soi": 0.5,
      "dmi": -0.014,
      "sst": {
        "nino34": 27.688,
        "karimata": 30.098,
        "makassar": 29.702,
        "jawa": 28.223,
        "maluku": 29.774
      },
      "sstAnom": {
        "nino34": -0.119,
        "karimata": 0.126,
        "makassar": 0.181,
        "jawa": 0.262,
        "maluku": 0.071
      },
      "split": "test"
    },
    {
      "period": "2025-07",
      "date": "2025-07",
      "oni": -0.11,
      "oni_anom": -0.11,
      "soi": 1.0,
      "dmi": -0.072,
      "sst": {
        "nino34": 27.191,
        "karimata": 29.544,
        "makassar": 29.209,
        "jawa": 27.019,
        "maluku": 29.578
      },
      "sstAnom": {
        "nino34": -0.135,
        "karimata": 0.071,
        "makassar": 0.042,
        "jawa": 0.032,
        "maluku": 0.198
      },
      "split": "test"
    },
    {
      "period": "2025-08",
      "date": "2025-08",
      "oni": -0.26,
      "oni_anom": -0.26,
      "soi": 0.7,
      "dmi": -0.42,
      "sst": {
        "nino34": 26.54,
        "karimata": 29.21,
        "makassar": 28.953,
        "jawa": 26.626,
        "maluku": 29.363
      },
      "sstAnom": {
        "nino34": -0.213,
        "karimata": 0.09,
        "makassar": -0.048,
        "jawa": 0.235,
        "maluku": 0.077
      },
      "split": "test"
    },
    {
      "period": "2025-09",
      "date": "2025-09",
      "oni": -0.43,
      "oni_anom": -0.43,
      "soi": 0.1,
      "dmi": -0.467,
      "sst": {
        "nino34": 26.313,
        "karimata": 29.271,
        "makassar": 29.294,
        "jawa": 26.88,
        "maluku": 29.51
      },
      "sstAnom": {
        "nino34": -0.263,
        "karimata": 0.133,
        "makassar": 0.095,
        "jawa": 0.284,
        "maluku": 0.092
      },
      "split": "test"
    },
    {
      "period": "2025-10",
      "date": "2025-10",
      "oni": -0.57,
      "oni_anom": -0.57,
      "soi": 1.9,
      "dmi": -0.448,
      "sst": {
        "nino34": 26.25,
        "karimata": 29.651,
        "makassar": 29.842,
        "jawa": 27.911,
        "maluku": 29.952
      },
      "sstAnom": {
        "nino34": -0.304,
        "karimata": 0.033,
        "makassar": 0.258,
        "jawa": 0.488,
        "maluku": 0.142
      },
      "split": "test"
    },
    {
      "period": "2025-11",
      "date": "2025-11",
      "oni": -0.61,
      "oni_anom": -0.61,
      "soi": 1.8,
      "dmi": -0.256,
      "sst": {
        "nino34": 26.057,
        "karimata": 29.568,
        "makassar": 29.64,
        "jawa": 28.354,
        "maluku": 29.866
      },
      "sstAnom": {
        "nino34": -0.49,
        "karimata": -0.183,
        "makassar": -0.133,
        "jawa": -0.002,
        "maluku": -0.136
      },
      "split": "test"
    },
    {
      "period": "2025-12",
      "date": "2025-12",
      "oni": -0.6,
      "oni_anom": -0.6,
      "soi": 0.0,
      "dmi": -0.017,
      "sst": {
        "nino34": 25.958,
        "karimata": 28.994,
        "makassar": 29.527,
        "jawa": 28.662,
        "maluku": 29.812
      },
      "sstAnom": {
        "nino34": -0.421,
        "karimata": -0.077,
        "makassar": -0.016,
        "jawa": 0.049,
        "maluku": -0.053
      },
      "split": "test"
    },
    {
      "period": "2026-01",
      "date": "2026-01",
      "oni": -0.39,
      "oni_anom": -0.39,
      "soi": 1.8,
      "dmi": 0.123,
      "sst": {
        "nino34": 25.935,
        "karimata": 27.895,
        "makassar": 29.251,
        "jawa": 28.5,
        "maluku": 29.568
      },
      "sstAnom": {
        "nino34": -0.65,
        "karimata": -0.566,
        "makassar": -0.003,
        "jawa": -0.369,
        "maluku": 0.083
      },
      "split": "test"
    },
    {
      "period": "2026-02",
      "date": "2026-02",
      "oni": -0.21,
      "oni_anom": -0.21,
      "soi": 2.4,
      "dmi": 0.529,
      "sst": {
        "nino34": 26.493,
        "karimata": 27.648,
        "makassar": 29.261,
        "jawa": 28.243,
        "maluku": 29.511
      },
      "sstAnom": {
        "nino34": -0.339,
        "karimata": -0.449,
        "makassar": 0.14,
        "jawa": -0.627,
        "maluku": 0.261
      },
      "split": "test"
    },
    {
      "period": "2026-03",
      "date": "2026-03",
      "oni": 0.11,
      "oni_anom": 0.11,
      "soi": 2.0,
      "dmi": 0.285,
      "sst": {
        "nino34": 27.206,
        "karimata": 28.396,
        "makassar": 29.221,
        "jawa": 28.719,
        "maluku": 29.211
      },
      "sstAnom": {
        "nino34": -0.202,
        "karimata": -0.31,
        "makassar": -0.155,
        "jawa": -0.516,
        "maluku": -0.226
      },
      "split": "test"
    }
  ],
  "regions": [
    {
      "id": "nino34",
      "name": "Pasifik Ni\u00f1o 3.4",
      "key": "nino34",
      "sst": 27.206,
      "anomaly": -0.202
    },
    {
      "id": "makassar",
      "name": "Selat Makassar",
      "key": "makassar",
      "sst": 29.221,
      "anomaly": -0.155
    },
    {
      "id": "karimata",
      "name": "Selat Karimata",
      "key": "karimata",
      "sst": 28.396,
      "anomaly": -0.31
    },
    {
      "id": "jawa",
      "name": "Selatan Jawa",
      "key": "jawa",
      "sst": 28.719,
      "anomaly": -0.516
    },
    {
      "id": "maluku",
      "name": "Maluku-Papua",
      "key": "maluku",
      "sst": 29.211,
      "anomaly": -0.226
    }
  ],
  "facts": {
    "counts": {
      "elNino": 32,
      "netral": 57,
      "laNina": 34
    },
    "warmestOni": {
      "value": 2.5,
      "date": "2016-01"
    },
    "coldestOni": {
      "value": -1.11,
      "date": "2020-11"
    },
    "warmestRegion": {
      "name": "Selat Makassar",
      "anomaly": -0.155
    }
  },
  "metrics": {
    "1": {
      "horizon_months": 1,
      "window_months": 12,
      "model": "causal_lstm_xgboost",
      "class_mapping": {
        "0": "La Nina",
        "1": "Neutral",
        "2": "El Nino"
      },
      "probabilities_calibrated": false,
      "validation": {
        "accuracy": 0.5384615384615384,
        "balanced_accuracy": 0.7083333333333334,
        "macro_f1": 0.5707070707070706,
        "confusion_matrix": [
          [
            1,
            0,
            0
          ],
          [
            1,
            3,
            0
          ],
          [
            0,
            5,
            3
          ]
        ],
        "log_loss": 1.0191903300776732,
        "multiclass_brier_score": 0.6260329032319992,
        "top_label_ece_10_bins": 0.10446044573417074,
        "mean_top_label_confidence": 0.553589559518374,
        "lstm_oni_rmse": 0.9934602493762092
      },
      "test": {
        "accuracy": 0.9375,
        "balanced_accuracy": 0.9615384615384616,
        "macro_f1": 0.9085714285714286,
        "confusion_matrix": [
          [
            3,
            0,
            0
          ],
          [
            1,
            12,
            0
          ],
          [
            0,
            0,
            0
          ]
        ],
        "log_loss": 0.5760054278598128,
        "multiclass_brier_score": 0.2962194490456652,
        "top_label_ece_10_bins": 0.34042187221348286,
        "mean_top_label_confidence": 0.5970781277865171,
        "lstm_oni_rmse": 0.19779171862933267
      }
    },
    "3": {
      "horizon_months": 3,
      "window_months": 12,
      "model": "causal_lstm_xgboost",
      "class_mapping": {
        "0": "La Nina",
        "1": "Neutral",
        "2": "El Nino"
      },
      "probabilities_calibrated": false,
      "validation": {
        "accuracy": 0.23076923076923078,
        "balanced_accuracy": 0.5,
        "macro_f1": 0.1875,
        "confusion_matrix": [
          [
            0,
            0,
            0
          ],
          [
            0,
            3,
            0
          ],
          [
            0,
            10,
            0
          ]
        ],
        "log_loss": 1.205522392088397,
        "multiclass_brier_score": 0.7346493915357813,
        "top_label_ece_10_bins": 0.19118712727840131,
        "mean_top_label_confidence": 0.4219563580476321,
        "lstm_oni_rmse": 1.2452632000297612
      },
      "test": {
        "accuracy": 0.6875,
        "balanced_accuracy": 0.3333333333333333,
        "macro_f1": 0.2716049382716049,
        "confusion_matrix": [
          [
            0,
            3,
            0
          ],
          [
            0,
            11,
            0
          ],
          [
            0,
            2,
            0
          ]
        ],
        "log_loss": 0.9856263143432117,
        "multiclass_brier_score": 0.59066059609985,
        "top_label_ece_10_bins": 0.29208432510495186,
        "mean_top_label_confidence": 0.39541567489504814,
        "lstm_oni_rmse": 0.4170920427616391
      }
    },
    "6": {
      "horizon_months": 6,
      "window_months": 12,
      "model": "causal_lstm_xgboost",
      "class_mapping": {
        "0": "La Nina",
        "1": "Neutral",
        "2": "El Nino"
      },
      "probabilities_calibrated": false,
      "validation": {
        "accuracy": 0.15384615384615385,
        "balanced_accuracy": 0.5,
        "macro_f1": 0.14814814814814814,
        "confusion_matrix": [
          [
            0,
            0,
            0
          ],
          [
            0,
            2,
            0
          ],
          [
            6,
            5,
            0
          ]
        ],
        "log_loss": 1.2694076345214,
        "multiclass_brier_score": 0.7729483504946756,
        "top_label_ece_10_bins": 0.22303137183189398,
        "mean_top_label_confidence": 0.3768775256780478,
        "lstm_oni_rmse": 1.2550546627396315
      },
      "test": {
        "accuracy": 0.5,
        "balanced_accuracy": 0.5027777777777778,
        "macro_f1": 0.47222222222222215,
        "confusion_matrix": [
          [
            1,
            0,
            2
          ],
          [
            4,
            3,
            1
          ],
          [
            0,
            1,
            4
          ]
        ],
        "log_loss": 1.0615500556846258,
        "multiclass_brier_score": 0.6410245542894273,
        "top_label_ece_10_bins": 0.13028939627110958,
        "mean_top_label_confidence": 0.3697106037288904,
        "lstm_oni_rmse": 0.98169082302393
      }
    },
    "9": {
      "horizon_months": 9,
      "window_months": 12,
      "model": "causal_lstm_xgboost",
      "class_mapping": {
        "0": "La Nina",
        "1": "Neutral",
        "2": "El Nino"
      },
      "probabilities_calibrated": false,
      "validation": {
        "accuracy": 0.38461538461538464,
        "balanced_accuracy": 0.5,
        "macro_f1": 0.3333333333333333,
        "confusion_matrix": [
          [
            0,
            0,
            0
          ],
          [
            0,
            5,
            0
          ],
          [
            8,
            0,
            0
          ]
        ],
        "log_loss": 0.9952365094641374,
        "multiclass_brier_score": 0.5772513822049975,
        "top_label_ece_10_bins": 0.3620856816952046,
        "mean_top_label_confidence": 0.5695782991556021,
        "lstm_oni_rmse": 1.400385549287221
      },
      "test": {
        "accuracy": 0.14285714285714285,
        "balanced_accuracy": 0.16666666666666666,
        "macro_f1": 0.125,
        "confusion_matrix": [
          [
            1,
            2,
            0
          ],
          [
            4,
            0,
            0
          ],
          [
            0,
            0,
            0
          ]
        ],
        "log_loss": 1.9156078735381858,
        "multiclass_brier_score": 1.1296716403816123,
        "top_label_ece_10_bins": 0.6022406475884573,
        "mean_top_label_confidence": 0.7450977904456002,
        "lstm_oni_rmse": 0.4379685224654492
      }
    },
    "12": {
      "horizon_months": 12,
      "window_months": 12,
      "model": "causal_lstm_xgboost",
      "class_mapping": {
        "0": "La Nina",
        "1": "Neutral",
        "2": "El Nino"
      },
      "probabilities_calibrated": false,
      "validation": {
        "accuracy": 0.46153846153846156,
        "balanced_accuracy": 0.4125,
        "macro_f1": 0.36752136752136755,
        "confusion_matrix": [
          [
            0,
            0,
            0
          ],
          [
            3,
            5,
            0
          ],
          [
            4,
            0,
            1
          ]
        ],
        "log_loss": 1.1273753378329994,
        "multiclass_brier_score": 0.7124704353907219,
        "top_label_ece_10_bins": 0.2828377324801225,
        "mean_top_label_confidence": 0.5541542837252984,
        "lstm_oni_rmse": 1.1311544749902303
      },
      "test": {
        "accuracy": 0.25,
        "balanced_accuracy": 0.5,
        "macro_f1": 0.2,
        "confusion_matrix": [
          [
            1,
            0,
            0
          ],
          [
            3,
            0,
            0
          ],
          [
            0,
            0,
            0
          ]
        ],
        "log_loss": 1.4427175603110296,
        "multiclass_brier_score": 0.9141380091712421,
        "top_label_ece_10_bins": 0.5759392380714417,
        "mean_top_label_confidence": 0.6797365546226501,
        "lstm_oni_rmse": 0.24171423797726405
      }
    }
  },
  "derived": {
    "1": {
      "kmrvMae": 0.162,
      "persistenceMae": 0.148,
      "samples": 16
    },
    "3": {
      "kmrvMae": 0.322,
      "persistenceMae": 0.185,
      "samples": 16
    },
    "6": {
      "kmrvMae": 0.772,
      "persistenceMae": 0.244,
      "samples": 16
    },
    "9": {
      "kmrvMae": 0.308,
      "persistenceMae": 0.15,
      "samples": 7
    },
    "12": {
      "kmrvMae": 0.196,
      "persistenceMae": 0.237,
      "samples": 4
    }
  },
  "testPredictions": {
    "1": [
      {
        "date": "2024-12-01",
        "actual_oni": -0.46,
        "lstm_oni": -0.581,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-01-01",
        "actual_oni": -0.22,
        "lstm_oni": -0.489,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-02-01",
        "actual_oni": -0.08,
        "lstm_oni": -0.243,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-03-01",
        "actual_oni": 0.02,
        "lstm_oni": -0.177,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-04-01",
        "actual_oni": -0.04,
        "lstm_oni": 0.003,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-05-01",
        "actual_oni": -0.02,
        "lstm_oni": -0.046,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-06-01",
        "actual_oni": -0.11,
        "lstm_oni": -0.142,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-07-01",
        "actual_oni": -0.26,
        "lstm_oni": -0.272,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-08-01",
        "actual_oni": -0.43,
        "lstm_oni": -0.466,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-09-01",
        "actual_oni": -0.57,
        "lstm_oni": -0.69,
        "actual_phase": 0,
        "predicted_phase": 0
      },
      {
        "date": "2025-10-01",
        "actual_oni": -0.61,
        "lstm_oni": -0.796,
        "actual_phase": 0,
        "predicted_phase": 0
      },
      {
        "date": "2025-11-01",
        "actual_oni": -0.6,
        "lstm_oni": -0.756,
        "actual_phase": 0,
        "predicted_phase": 0
      },
      {
        "date": "2025-12-01",
        "actual_oni": -0.39,
        "lstm_oni": -0.629,
        "actual_phase": 1,
        "predicted_phase": 0
      },
      {
        "date": "2026-01-01",
        "actual_oni": -0.21,
        "lstm_oni": -0.5,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2026-02-01",
        "actual_oni": 0.11,
        "lstm_oni": -0.206,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2026-03-01",
        "actual_oni": 0.46,
        "lstm_oni": 0.067,
        "actual_phase": 1,
        "predicted_phase": 1
      }
    ],
    "3": [
      {
        "date": "2024-12-01",
        "actual_oni": -0.08,
        "lstm_oni": -0.384,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-01-01",
        "actual_oni": 0.02,
        "lstm_oni": -0.187,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-02-01",
        "actual_oni": -0.04,
        "lstm_oni": 0.085,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-03-01",
        "actual_oni": -0.02,
        "lstm_oni": 0.078,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-04-01",
        "actual_oni": -0.11,
        "lstm_oni": 0.082,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-05-01",
        "actual_oni": -0.26,
        "lstm_oni": -0.186,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-06-01",
        "actual_oni": -0.43,
        "lstm_oni": -0.411,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-07-01",
        "actual_oni": -0.57,
        "lstm_oni": -0.589,
        "actual_phase": 0,
        "predicted_phase": 1
      },
      {
        "date": "2025-08-01",
        "actual_oni": -0.61,
        "lstm_oni": -0.77,
        "actual_phase": 0,
        "predicted_phase": 1
      },
      {
        "date": "2025-09-01",
        "actual_oni": -0.6,
        "lstm_oni": -0.858,
        "actual_phase": 0,
        "predicted_phase": 1
      },
      {
        "date": "2025-10-01",
        "actual_oni": -0.39,
        "lstm_oni": -0.823,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-11-01",
        "actual_oni": -0.21,
        "lstm_oni": -0.664,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-12-01",
        "actual_oni": 0.11,
        "lstm_oni": -0.451,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2026-01-01",
        "actual_oni": 0.46,
        "lstm_oni": -0.091,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2026-02-01",
        "actual_oni": 0.95,
        "lstm_oni": 0.225,
        "actual_phase": 2,
        "predicted_phase": 1
      },
      {
        "date": "2026-03-01",
        "actual_oni": 1.39,
        "lstm_oni": 0.415,
        "actual_phase": 2,
        "predicted_phase": 1
      }
    ],
    "6": [
      {
        "date": "2024-12-01",
        "actual_oni": -0.02,
        "lstm_oni": -0.198,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-01-01",
        "actual_oni": -0.11,
        "lstm_oni": -0.083,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-02-01",
        "actual_oni": -0.26,
        "lstm_oni": -0.023,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-03-01",
        "actual_oni": -0.43,
        "lstm_oni": -0.258,
        "actual_phase": 1,
        "predicted_phase": 2
      },
      {
        "date": "2025-04-01",
        "actual_oni": -0.57,
        "lstm_oni": -0.434,
        "actual_phase": 0,
        "predicted_phase": 2
      },
      {
        "date": "2025-05-01",
        "actual_oni": -0.61,
        "lstm_oni": -0.874,
        "actual_phase": 0,
        "predicted_phase": 2
      },
      {
        "date": "2025-06-01",
        "actual_oni": -0.6,
        "lstm_oni": -0.986,
        "actual_phase": 0,
        "predicted_phase": 0
      },
      {
        "date": "2025-07-01",
        "actual_oni": -0.39,
        "lstm_oni": -0.982,
        "actual_phase": 1,
        "predicted_phase": 0
      },
      {
        "date": "2025-08-01",
        "actual_oni": -0.21,
        "lstm_oni": -0.893,
        "actual_phase": 1,
        "predicted_phase": 0
      },
      {
        "date": "2025-09-01",
        "actual_oni": 0.11,
        "lstm_oni": -0.713,
        "actual_phase": 1,
        "predicted_phase": 0
      },
      {
        "date": "2025-10-01",
        "actual_oni": 0.46,
        "lstm_oni": -0.54,
        "actual_phase": 1,
        "predicted_phase": 0
      },
      {
        "date": "2025-11-01",
        "actual_oni": 0.95,
        "lstm_oni": -0.257,
        "actual_phase": 2,
        "predicted_phase": 1
      },
      {
        "date": "2025-12-01",
        "actual_oni": 1.39,
        "lstm_oni": -0.127,
        "actual_phase": 2,
        "predicted_phase": 2
      },
      {
        "date": "2026-01-01",
        "actual_oni": 1.8,
        "lstm_oni": 0.188,
        "actual_phase": 2,
        "predicted_phase": 2
      },
      {
        "date": "2026-02-01",
        "actual_oni": 2.16,
        "lstm_oni": 0.423,
        "actual_phase": 2,
        "predicted_phase": 2
      },
      {
        "date": "2026-03-01",
        "actual_oni": 2.46,
        "lstm_oni": 0.673,
        "actual_phase": 2,
        "predicted_phase": 2
      }
    ],
    "9": [
      {
        "date": "2024-12-01",
        "actual_oni": -0.43,
        "lstm_oni": -0.525,
        "actual_phase": 1,
        "predicted_phase": 0
      },
      {
        "date": "2025-01-01",
        "actual_oni": -0.57,
        "lstm_oni": -0.5,
        "actual_phase": 0,
        "predicted_phase": 1
      },
      {
        "date": "2025-02-01",
        "actual_oni": -0.61,
        "lstm_oni": -0.502,
        "actual_phase": 0,
        "predicted_phase": 1
      },
      {
        "date": "2025-03-01",
        "actual_oni": -0.6,
        "lstm_oni": -0.668,
        "actual_phase": 0,
        "predicted_phase": 0
      },
      {
        "date": "2025-04-01",
        "actual_oni": -0.39,
        "lstm_oni": -0.661,
        "actual_phase": 1,
        "predicted_phase": 0
      },
      {
        "date": "2025-05-01",
        "actual_oni": -0.21,
        "lstm_oni": -0.838,
        "actual_phase": 1,
        "predicted_phase": 0
      },
      {
        "date": "2025-06-01",
        "actual_oni": 0.11,
        "lstm_oni": -0.809,
        "actual_phase": 1,
        "predicted_phase": 0
      }
    ],
    "12": [
      {
        "date": "2024-12-01",
        "actual_oni": -0.6,
        "lstm_oni": -0.297,
        "actual_phase": 0,
        "predicted_phase": 0
      },
      {
        "date": "2025-01-01",
        "actual_oni": -0.39,
        "lstm_oni": -0.302,
        "actual_phase": 1,
        "predicted_phase": 0
      },
      {
        "date": "2025-02-01",
        "actual_oni": -0.21,
        "lstm_oni": -0.238,
        "actual_phase": 1,
        "predicted_phase": 0
      },
      {
        "date": "2025-03-01",
        "actual_oni": 0.11,
        "lstm_oni": -0.255,
        "actual_phase": 1,
        "predicted_phase": 0
      }
    ]
  },
  "heatmap": [
    {
      "year": 2016,
      "months": [
        {
          "month": 1,
          "date": "2016-01",
          "value": 2.5
        },
        {
          "month": 2,
          "date": "2016-02",
          "value": 2.21
        },
        {
          "month": 3,
          "date": "2016-03",
          "value": 1.69
        },
        {
          "month": 4,
          "date": "2016-04",
          "value": 1.11
        },
        {
          "month": 5,
          "date": "2016-05",
          "value": 0.57
        },
        {
          "month": 6,
          "date": "2016-06",
          "value": 0.09
        },
        {
          "month": 7,
          "date": "2016-07",
          "value": -0.19
        },
        {
          "month": 8,
          "date": "2016-08",
          "value": -0.34
        },
        {
          "month": 9,
          "date": "2016-09",
          "value": -0.42
        },
        {
          "month": 10,
          "date": "2016-10",
          "value": -0.51
        },
        {
          "month": 11,
          "date": "2016-11",
          "value": -0.49
        },
        {
          "month": 12,
          "date": "2016-12",
          "value": -0.37
        }
      ]
    },
    {
      "year": 2017,
      "months": [
        {
          "month": 1,
          "date": "2017-01",
          "value": -0.08
        },
        {
          "month": 2,
          "date": "2017-02",
          "value": 0.08
        },
        {
          "month": 3,
          "date": "2017-03",
          "value": 0.27
        },
        {
          "month": 4,
          "date": "2017-04",
          "value": 0.32
        },
        {
          "month": 5,
          "date": "2017-05",
          "value": 0.35
        },
        {
          "month": 6,
          "date": "2017-06",
          "value": 0.32
        },
        {
          "month": 7,
          "date": "2017-07",
          "value": 0.14
        },
        {
          "month": 8,
          "date": "2017-08",
          "value": -0.07
        },
        {
          "month": 9,
          "date": "2017-09",
          "value": -0.23
        },
        {
          "month": 10,
          "date": "2017-10",
          "value": -0.44
        },
        {
          "month": 11,
          "date": "2017-11",
          "value": -0.61
        },
        {
          "month": 12,
          "date": "2017-12",
          "value": -0.76
        }
      ]
    },
    {
      "year": 2018,
      "months": [
        {
          "month": 1,
          "date": "2018-01",
          "value": -0.71
        },
        {
          "month": 2,
          "date": "2018-02",
          "value": -0.67
        },
        {
          "month": 3,
          "date": "2018-03",
          "value": -0.55
        },
        {
          "month": 4,
          "date": "2018-04",
          "value": -0.35
        },
        {
          "month": 5,
          "date": "2018-05",
          "value": -0.07
        },
        {
          "month": 6,
          "date": "2018-06",
          "value": 0.13
        },
        {
          "month": 7,
          "date": "2018-07",
          "value": 0.2
        },
        {
          "month": 8,
          "date": "2018-08",
          "value": 0.3
        },
        {
          "month": 9,
          "date": "2018-09",
          "value": 0.52
        },
        {
          "month": 10,
          "date": "2018-10",
          "value": 0.82
        },
        {
          "month": 11,
          "date": "2018-11",
          "value": 1.04
        },
        {
          "month": 12,
          "date": "2018-12",
          "value": 1.05
        }
      ]
    },
    {
      "year": 2019,
      "months": [
        {
          "month": 1,
          "date": "2019-01",
          "value": 0.99
        },
        {
          "month": 2,
          "date": "2019-02",
          "value": 0.94
        },
        {
          "month": 3,
          "date": "2019-03",
          "value": 0.87
        },
        {
          "month": 4,
          "date": "2019-04",
          "value": 0.82
        },
        {
          "month": 5,
          "date": "2019-05",
          "value": 0.71
        },
        {
          "month": 6,
          "date": "2019-06",
          "value": 0.59
        },
        {
          "month": 7,
          "date": "2019-07",
          "value": 0.38
        },
        {
          "month": 8,
          "date": "2019-08",
          "value": 0.2
        },
        {
          "month": 9,
          "date": "2019-09",
          "value": 0.31
        },
        {
          "month": 10,
          "date": "2019-10",
          "value": 0.51
        },
        {
          "month": 11,
          "date": "2019-11",
          "value": 0.72
        },
        {
          "month": 12,
          "date": "2019-12",
          "value": 0.75
        }
      ]
    },
    {
      "year": 2020,
      "months": [
        {
          "month": 1,
          "date": "2020-01",
          "value": 0.71
        },
        {
          "month": 2,
          "date": "2020-02",
          "value": 0.66
        },
        {
          "month": 3,
          "date": "2020-03",
          "value": 0.57
        },
        {
          "month": 4,
          "date": "2020-04",
          "value": 0.33
        },
        {
          "month": 5,
          "date": "2020-05",
          "value": 0.04
        },
        {
          "month": 6,
          "date": "2020-06",
          "value": -0.18
        },
        {
          "month": 7,
          "date": "2020-07",
          "value": -0.29
        },
        {
          "month": 8,
          "date": "2020-08",
          "value": -0.43
        },
        {
          "month": 9,
          "date": "2020-09",
          "value": -0.77
        },
        {
          "month": 10,
          "date": "2020-10",
          "value": -1.0
        },
        {
          "month": 11,
          "date": "2020-11",
          "value": -1.11
        },
        {
          "month": 12,
          "date": "2020-12",
          "value": -1.06
        }
      ]
    },
    {
      "year": 2021,
      "months": [
        {
          "month": 1,
          "date": "2021-01",
          "value": -0.99
        },
        {
          "month": 2,
          "date": "2021-02",
          "value": -0.85
        },
        {
          "month": 3,
          "date": "2021-03",
          "value": -0.74
        },
        {
          "month": 4,
          "date": "2021-04",
          "value": -0.56
        },
        {
          "month": 5,
          "date": "2021-05",
          "value": -0.4
        },
        {
          "month": 6,
          "date": "2021-06",
          "value": -0.31
        },
        {
          "month": 7,
          "date": "2021-07",
          "value": -0.35
        },
        {
          "month": 8,
          "date": "2021-08",
          "value": -0.46
        },
        {
          "month": 9,
          "date": "2021-09",
          "value": -0.64
        },
        {
          "month": 10,
          "date": "2021-10",
          "value": -0.77
        },
        {
          "month": 11,
          "date": "2021-11",
          "value": -0.91
        },
        {
          "month": 12,
          "date": "2021-12",
          "value": -0.83
        }
      ]
    },
    {
      "year": 2022,
      "months": [
        {
          "month": 1,
          "date": "2022-01",
          "value": -0.76
        },
        {
          "month": 2,
          "date": "2022-02",
          "value": -0.68
        },
        {
          "month": 3,
          "date": "2022-03",
          "value": -0.77
        },
        {
          "month": 4,
          "date": "2022-04",
          "value": -0.86
        },
        {
          "month": 5,
          "date": "2022-05",
          "value": -0.83
        },
        {
          "month": 6,
          "date": "2022-06",
          "value": -0.73
        },
        {
          "month": 7,
          "date": "2022-07",
          "value": -0.7
        },
        {
          "month": 8,
          "date": "2022-08",
          "value": -0.78
        },
        {
          "month": 9,
          "date": "2022-09",
          "value": -0.87
        },
        {
          "month": 10,
          "date": "2022-10",
          "value": -0.89
        },
        {
          "month": 11,
          "date": "2022-11",
          "value": -0.82
        },
        {
          "month": 12,
          "date": "2022-12",
          "value": -0.7
        }
      ]
    },
    {
      "year": 2023,
      "months": [
        {
          "month": 1,
          "date": "2023-01",
          "value": -0.55
        },
        {
          "month": 2,
          "date": "2023-02",
          "value": -0.33
        },
        {
          "month": 3,
          "date": "2023-03",
          "value": -0.11
        },
        {
          "month": 4,
          "date": "2023-04",
          "value": 0.19
        },
        {
          "month": 5,
          "date": "2023-05",
          "value": 0.46
        },
        {
          "month": 6,
          "date": "2023-06",
          "value": 0.73
        },
        {
          "month": 7,
          "date": "2023-07",
          "value": 1.0
        },
        {
          "month": 8,
          "date": "2023-08",
          "value": 1.25
        },
        {
          "month": 9,
          "date": "2023-09",
          "value": 1.5
        },
        {
          "month": 10,
          "date": "2023-10",
          "value": 1.74
        },
        {
          "month": 11,
          "date": "2023-11",
          "value": 1.9
        },
        {
          "month": 12,
          "date": "2023-12",
          "value": 1.99
        }
      ]
    },
    {
      "year": 2024,
      "months": [
        {
          "month": 1,
          "date": "2024-01",
          "value": 1.84
        },
        {
          "month": 2,
          "date": "2024-02",
          "value": 1.53
        },
        {
          "month": 3,
          "date": "2024-03",
          "value": 1.18
        },
        {
          "month": 4,
          "date": "2024-04",
          "value": 0.77
        },
        {
          "month": 5,
          "date": "2024-05",
          "value": 0.43
        },
        {
          "month": 6,
          "date": "2024-06",
          "value": 0.18
        },
        {
          "month": 7,
          "date": "2024-07",
          "value": 0.06
        },
        {
          "month": 8,
          "date": "2024-08",
          "value": -0.04
        },
        {
          "month": 9,
          "date": "2024-09",
          "value": -0.12
        },
        {
          "month": 10,
          "date": "2024-10",
          "value": -0.19
        },
        {
          "month": 11,
          "date": "2024-11",
          "value": -0.29
        },
        {
          "month": 12,
          "date": "2024-12",
          "value": -0.43
        }
      ]
    },
    {
      "year": 2025,
      "months": [
        {
          "month": 1,
          "date": "2025-01",
          "value": -0.46
        },
        {
          "month": 2,
          "date": "2025-02",
          "value": -0.22
        },
        {
          "month": 3,
          "date": "2025-03",
          "value": -0.08
        },
        {
          "month": 4,
          "date": "2025-04",
          "value": 0.02
        },
        {
          "month": 5,
          "date": "2025-05",
          "value": -0.04
        },
        {
          "month": 6,
          "date": "2025-06",
          "value": -0.02
        },
        {
          "month": 7,
          "date": "2025-07",
          "value": -0.11
        },
        {
          "month": 8,
          "date": "2025-08",
          "value": -0.26
        },
        {
          "month": 9,
          "date": "2025-09",
          "value": -0.43
        },
        {
          "month": 10,
          "date": "2025-10",
          "value": -0.57
        },
        {
          "month": 11,
          "date": "2025-11",
          "value": -0.61
        },
        {
          "month": 12,
          "date": "2025-12",
          "value": -0.6
        }
      ]
    },
    {
      "year": 2026,
      "months": [
        {
          "month": 1,
          "date": "2026-01",
          "value": -0.39
        },
        {
          "month": 2,
          "date": "2026-02",
          "value": -0.21
        },
        {
          "month": 3,
          "date": "2026-03",
          "value": 0.11
        },
        {
          "month": 4,
          "date": "2026-04",
          "value": null
        },
        {
          "month": 5,
          "date": "2026-05",
          "value": null
        },
        {
          "month": 6,
          "date": "2026-06",
          "value": null
        },
        {
          "month": 7,
          "date": "2026-07",
          "value": null
        },
        {
          "month": 8,
          "date": "2026-08",
          "value": null
        },
        {
          "month": 9,
          "date": "2026-09",
          "value": null
        },
        {
          "month": 10,
          "date": "2026-10",
          "value": null
        },
        {
          "month": 11,
          "date": "2026-11",
          "value": null
        },
        {
          "month": 12,
          "date": "2026-12",
          "value": null
        }
      ]
    }
  ],
  "annualPhases": [
    {
      "year": 2016,
      "netral": 6,
      "elNino": 5,
      "laNina": 1,
      "total": 12
    },
    {
      "year": 2017,
      "netral": 10,
      "elNino": 0,
      "laNina": 2,
      "total": 12
    },
    {
      "year": 2018,
      "netral": 5,
      "elNino": 4,
      "laNina": 3,
      "total": 12
    },
    {
      "year": 2019,
      "netral": 3,
      "elNino": 9,
      "laNina": 0,
      "total": 12
    },
    {
      "year": 2020,
      "netral": 5,
      "elNino": 3,
      "laNina": 4,
      "total": 12
    },
    {
      "year": 2021,
      "netral": 4,
      "elNino": 0,
      "laNina": 8,
      "total": 12
    },
    {
      "year": 2022,
      "netral": 0,
      "elNino": 0,
      "laNina": 12,
      "total": 12
    },
    {
      "year": 2023,
      "netral": 4,
      "elNino": 7,
      "laNina": 1,
      "total": 12
    },
    {
      "year": 2024,
      "netral": 8,
      "elNino": 4,
      "laNina": 0,
      "total": 12
    },
    {
      "year": 2025,
      "netral": 9,
      "elNino": 0,
      "laNina": 3,
      "total": 12
    },
    {
      "year": 2026,
      "netral": 3,
      "elNino": 0,
      "laNina": 0,
      "total": 3
    }
  ],
  "forecastSeries": {
    "1": [
      {
        "date": "12/25",
        "actual": -0.6,
        "prediction": null,
        "isPrediction": false
      },
      {
        "date": "01/26",
        "actual": -0.39,
        "prediction": null,
        "isPrediction": false
      },
      {
        "date": "02/26",
        "actual": -0.21,
        "prediction": null,
        "isPrediction": false
      },
      {
        "date": "03/26",
        "actual": 0.11,
        "prediction": 0.11,
        "isPrediction": false
      },
      {
        "date": "04/26",
        "actual": 0.46,
        "prediction": 0.067,
        "isPrediction": true
      }
    ],
    "3": [
      {
        "date": "12/25",
        "actual": -0.6,
        "prediction": null,
        "isPrediction": false
      },
      {
        "date": "01/26",
        "actual": -0.39,
        "prediction": null,
        "isPrediction": false
      },
      {
        "date": "02/26",
        "actual": -0.21,
        "prediction": null,
        "isPrediction": false
      },
      {
        "date": "03/26",
        "actual": 0.11,
        "prediction": 0.11,
        "isPrediction": false
      },
      {
        "date": "04/26",
        "actual": 0.46,
        "prediction": 0.067,
        "isPrediction": true
      },
      {
        "date": "05/26",
        "actual": 0.95,
        "prediction": 0.241,
        "isPrediction": true
      },
      {
        "date": "06/26",
        "actual": 1.39,
        "prediction": 0.415,
        "isPrediction": true
      }
    ],
    "6": [
      {
        "date": "12/25",
        "actual": -0.6,
        "prediction": null,
        "isPrediction": false
      },
      {
        "date": "01/26",
        "actual": -0.39,
        "prediction": null,
        "isPrediction": false
      },
      {
        "date": "02/26",
        "actual": -0.21,
        "prediction": null,
        "isPrediction": false
      },
      {
        "date": "03/26",
        "actual": 0.11,
        "prediction": 0.11,
        "isPrediction": false
      },
      {
        "date": "04/26",
        "actual": 0.46,
        "prediction": 0.067,
        "isPrediction": true
      },
      {
        "date": "05/26",
        "actual": 0.95,
        "prediction": 0.241,
        "isPrediction": true
      },
      {
        "date": "06/26",
        "actual": 1.39,
        "prediction": 0.415,
        "isPrediction": true
      },
      {
        "date": "07/26",
        "actual": 1.8,
        "prediction": 0.501,
        "isPrediction": true
      },
      {
        "date": "08/26",
        "actual": 2.16,
        "prediction": 0.587,
        "isPrediction": true
      },
      {
        "date": "09/26",
        "actual": 2.46,
        "prediction": 0.673,
        "isPrediction": true
      }
    ],
    "9": [
      {
        "date": "12/25",
        "actual": -0.6,
        "prediction": null,
        "isPrediction": false
      },
      {
        "date": "01/26",
        "actual": -0.39,
        "prediction": null,
        "isPrediction": false
      },
      {
        "date": "02/26",
        "actual": -0.21,
        "prediction": null,
        "isPrediction": false
      },
      {
        "date": "03/26",
        "actual": 0.11,
        "prediction": 0.11,
        "isPrediction": false
      },
      {
        "date": "04/26",
        "actual": 0.46,
        "prediction": 0.067,
        "isPrediction": true
      },
      {
        "date": "05/26",
        "actual": 0.95,
        "prediction": 0.241,
        "isPrediction": true
      },
      {
        "date": "06/26",
        "actual": 1.39,
        "prediction": 0.415,
        "isPrediction": true
      },
      {
        "date": "07/26",
        "actual": 1.8,
        "prediction": 0.501,
        "isPrediction": true
      },
      {
        "date": "08/26",
        "actual": 2.16,
        "prediction": 0.587,
        "isPrediction": true
      },
      {
        "date": "09/26",
        "actual": 2.46,
        "prediction": 0.673,
        "isPrediction": true
      },
      {
        "date": "10/26",
        "actual": null,
        "prediction": 0.179,
        "isPrediction": true
      },
      {
        "date": "11/26",
        "actual": null,
        "prediction": -0.315,
        "isPrediction": true
      },
      {
        "date": "12/26",
        "actual": null,
        "prediction": -0.809,
        "isPrediction": true
      }
    ],
    "12": [
      {
        "date": "12/25",
        "actual": -0.6,
        "prediction": null,
        "isPrediction": false
      },
      {
        "date": "01/26",
        "actual": -0.39,
        "prediction": null,
        "isPrediction": false
      },
      {
        "date": "02/26",
        "actual": -0.21,
        "prediction": null,
        "isPrediction": false
      },
      {
        "date": "03/26",
        "actual": 0.11,
        "prediction": 0.11,
        "isPrediction": false
      },
      {
        "date": "04/26",
        "actual": 0.46,
        "prediction": 0.067,
        "isPrediction": true
      },
      {
        "date": "05/26",
        "actual": 0.95,
        "prediction": 0.241,
        "isPrediction": true
      },
      {
        "date": "06/26",
        "actual": 1.39,
        "prediction": 0.415,
        "isPrediction": true
      },
      {
        "date": "07/26",
        "actual": 1.8,
        "prediction": 0.501,
        "isPrediction": true
      },
      {
        "date": "08/26",
        "actual": 2.16,
        "prediction": 0.587,
        "isPrediction": true
      },
      {
        "date": "09/26",
        "actual": 2.46,
        "prediction": 0.673,
        "isPrediction": true
      },
      {
        "date": "10/26",
        "actual": null,
        "prediction": 0.179,
        "isPrediction": true
      },
      {
        "date": "11/26",
        "actual": null,
        "prediction": -0.315,
        "isPrediction": true
      },
      {
        "date": "12/26",
        "actual": null,
        "prediction": -0.809,
        "isPrediction": true
      },
      {
        "date": "01/27",
        "actual": null,
        "prediction": -0.624,
        "isPrediction": true
      },
      {
        "date": "02/27",
        "actual": null,
        "prediction": -0.44,
        "isPrediction": true
      },
      {
        "date": "03/27",
        "actual": null,
        "prediction": -0.255,
        "isPrediction": true
      }
    ]
  },
  "evaluation": {
    "1": {
      "label": "1 bulan",
      "verdict": "Andal",
      "tone": "good",
      "accuracy": {
        "val": 53.8,
        "test": 93.8
      },
      "balanced": {
        "val": 70.8,
        "test": 96.2
      },
      "f1": {
        "val": 57.1,
        "test": 90.9
      },
      "rmse": {
        "val": 0.993,
        "test": 0.198
      },
      "maeModel": 0.162,
      "maeBaseline": 0.148,
      "matrix": [
        [
          3,
          0,
          0
        ],
        [
          1,
          12,
          0
        ],
        [
          0,
          0,
          0
        ]
      ],
      "matrixNote": "15 benar dari 16. Prediksi stabil pada variasi fase."
    },
    "3": {
      "label": "3 bulan",
      "verdict": "Trivial majority class",
      "tone": "warn",
      "accuracy": {
        "val": 23.1,
        "test": 68.8
      },
      "balanced": {
        "val": 50.0,
        "test": 33.3
      },
      "f1": {
        "val": 18.8,
        "test": 27.2
      },
      "rmse": {
        "val": 1.245,
        "test": 0.417
      },
      "maeModel": 0.322,
      "maeBaseline": 0.185,
      "matrix": [
        [
          0,
          3,
          0
        ],
        [
          0,
          11,
          0
        ],
        [
          0,
          2,
          0
        ]
      ],
      "matrixNote": "Akurasi 68.8% semu \u2014 model memprediksi mayoritas sampel uji sebagai Netral."
    },
    "6": {
      "label": "6 bulan",
      "verdict": "Gagal",
      "tone": "bad",
      "accuracy": {
        "val": 15.4,
        "test": 50.0
      },
      "balanced": {
        "val": 50.0,
        "test": 50.3
      },
      "f1": {
        "val": 14.8,
        "test": 47.2
      },
      "rmse": {
        "val": 1.255,
        "test": 0.982
      },
      "maeModel": 0.772,
      "maeBaseline": 0.244,
      "matrix": [
        [
          1,
          0,
          2
        ],
        [
          4,
          3,
          1
        ],
        [
          0,
          1,
          4
        ]
      ],
      "matrixNote": "8 benar dari 16. Kinerja rendah akibat barrier musim semi ENSO."
    },
    "9": {
      "label": "9 bulan",
      "verdict": "Tidak Andal",
      "tone": "bad",
      "accuracy": {
        "val": 38.5,
        "test": 14.3
      },
      "balanced": {
        "val": 50.0,
        "test": 16.7
      },
      "f1": {
        "val": 33.3,
        "test": 12.5
      },
      "rmse": {
        "val": 1.4,
        "test": 0.438
      },
      "maeModel": 0.308,
      "maeBaseline": 0.15,
      "matrix": [
        [
          1,
          2,
          0
        ],
        [
          4,
          0,
          0
        ],
        [
          0,
          0,
          0
        ]
      ],
      "matrixNote": "1 benar dari 7. Kinerja rendah akibat akumulasi galat multi-step."
    },
    "12": {
      "label": "12 bulan",
      "verdict": "Eksperimental / Noise",
      "tone": "bad",
      "accuracy": {
        "val": 46.2,
        "test": 25.0
      },
      "balanced": {
        "val": 41.2,
        "test": 50.0
      },
      "f1": {
        "val": 36.8,
        "test": 20.0
      },
      "rmse": {
        "val": 1.131,
        "test": 0.242
      },
      "maeModel": 0.196,
      "maeBaseline": 0.237,
      "matrix": [
        [
          1,
          0,
          0
        ],
        [
          3,
          0,
          0
        ],
        [
          0,
          0,
          0
        ]
      ],
      "matrixNote": "1 benar dari 4. Batas prediktabilitas model empiris terlampaui."
    }
  }
};

export const latestSnapshot = realData.latestSnapshot;
export const domainAnomalies = realData.domainAnomalies;
export const history = realData.history;
export const evaluation = realData.evaluation;

export const meta = realData.meta;
export const latest = realData.latest;
export const regions = realData.regions;
export const facts = realData.facts;
export const metrics = realData.metrics;
export const derived = realData.derived;
export const testPredictions = realData.testPredictions;
export const heatmap = realData.heatmap;
export const annualPhases = realData.annualPhases;
export const forecastSeries = realData.forecastSeries;
