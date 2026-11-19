// Generated from dataset/features_master_unscaled.csv and model/ artifacts. Do not hand-edit.
export const realData = {
  "meta": {
    "datasetStart": "2016-01",
    "datasetEnd": "2025-06",
    "rows": 114,
    "source": "dataset/features_master_unscaled.csv",
    "bestValidationHorizon": 1,
    "phaseRule": "El Nino >= +0,5 C; La Nina <= -0,5 C; Netral di antaranya",
    "climatology": "Anomali SST = SST - rata-rata bulan yang sama (2016-2025)"
  },
  "latest": {
    "date": "2025-06",
    "oni": -0.02,
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
    "split": "test",
    "phase": "Netral",
    "previousDate": "2025-05",
    "deltaOni": 0.02
  },
  "history": [
    {
      "date": "2016-01",
      "oni": 2.5,
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
        "nino34": 2.374,
        "karimata": 0.8,
        "makassar": 0.322,
        "jawa": 0.974,
        "maluku": -0.5
      },
      "split": "train"
    },
    {
      "date": "2016-02",
      "oni": 2.21,
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
        "nino34": 2.09,
        "karimata": 0.777,
        "makassar": 0.095,
        "jawa": 0.882,
        "maluku": -0.415
      },
      "split": "train"
    },
    {
      "date": "2016-03",
      "oni": 1.69,
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
        "nino34": 1.39,
        "karimata": 0.421,
        "makassar": 0.331,
        "jawa": 1.147,
        "maluku": -0.401
      },
      "split": "train"
    },
    {
      "date": "2016-04",
      "oni": 1.11,
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
      "date": "2016-05",
      "oni": 0.57,
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
      "date": "2016-06",
      "oni": 0.09,
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
      "date": "2016-07",
      "oni": -0.19,
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
        "nino34": -0.557,
        "karimata": 0.599,
        "makassar": 0.351,
        "jawa": 1.801,
        "maluku": 0.022
      },
      "split": "train"
    },
    {
      "date": "2016-08",
      "oni": -0.34,
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
        "nino34": -0.45,
        "karimata": 0.627,
        "makassar": 0.215,
        "jawa": 1.692,
        "maluku": -0.01
      },
      "split": "train"
    },
    {
      "date": "2016-09",
      "oni": -0.42,
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
        "nino34": -0.35,
        "karimata": 0.726,
        "makassar": 0.274,
        "jawa": 1.431,
        "maluku": 0.178
      },
      "split": "train"
    },
    {
      "date": "2016-10",
      "oni": -0.51,
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
        "nino34": -0.598,
        "karimata": 0.191,
        "makassar": -0.029,
        "jawa": 0.96,
        "maluku": 0.118
      },
      "split": "train"
    },
    {
      "date": "2016-11",
      "oni": -0.49,
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
        "nino34": -0.5,
        "karimata": -0.293,
        "makassar": -0.316,
        "jawa": 0.508,
        "maluku": -0.139
      },
      "split": "train"
    },
    {
      "date": "2016-12",
      "oni": -0.37,
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
        "nino34": -0.195,
        "karimata": 0.049,
        "makassar": -0.229,
        "jawa": 0.153,
        "maluku": -0.097
      },
      "split": "train"
    },
    {
      "date": "2017-01",
      "oni": -0.08,
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
        "nino34": -0.43,
        "karimata": 0.313,
        "makassar": -0.277,
        "jawa": -0.313,
        "maluku": -0.099
      },
      "split": "train"
    },
    {
      "date": "2017-02",
      "oni": 0.08,
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
        "nino34": -0.097,
        "karimata": -0.009,
        "makassar": -0.315,
        "jawa": -0.079,
        "maluku": -0.18
      },
      "split": "train"
    },
    {
      "date": "2017-03",
      "oni": 0.27,
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
        "nino34": -0.057,
        "karimata": -0.048,
        "makassar": -0.195,
        "jawa": -0.206,
        "maluku": -0.218
      },
      "split": "train"
    },
    {
      "date": "2017-04",
      "oni": 0.32,
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
      "date": "2017-05",
      "oni": 0.35,
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
      "date": "2017-06",
      "oni": 0.32,
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
      "date": "2017-07",
      "oni": 0.14,
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
        "nino34": 0.19,
        "karimata": -0.245,
        "makassar": -0.187,
        "jawa": -0.674,
        "maluku": -0.016
      },
      "split": "train"
    },
    {
      "date": "2017-08",
      "oni": -0.07,
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
        "nino34": 0.002,
        "karimata": -0.306,
        "makassar": -0.19,
        "jawa": -0.598,
        "maluku": -0.117
      },
      "split": "train"
    },
    {
      "date": "2017-09",
      "oni": -0.23,
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
        "nino34": -0.224,
        "karimata": -0.107,
        "makassar": 0.009,
        "jawa": -0.413,
        "maluku": -0.083
      },
      "split": "train"
    },
    {
      "date": "2017-10",
      "oni": -0.44,
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
        "nino34": -0.26,
        "karimata": -0.075,
        "makassar": -0.245,
        "jawa": -0.592,
        "maluku": 0.013
      },
      "split": "train"
    },
    {
      "date": "2017-11",
      "oni": -0.61,
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
        "nino34": -0.779,
        "karimata": -0.297,
        "makassar": -0.216,
        "jawa": -0.03,
        "maluku": -0.047
      },
      "split": "train"
    },
    {
      "date": "2017-12",
      "oni": -0.76,
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
        "nino34": -0.8,
        "karimata": -0.632,
        "makassar": -0.265,
        "jawa": -0.504,
        "maluku": -0.034
      },
      "split": "train"
    },
    {
      "date": "2018-01",
      "oni": -0.71,
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
        "nino34": -0.869,
        "karimata": -0.473,
        "makassar": -0.385,
        "jawa": -0.408,
        "maluku": -0.005
      },
      "split": "train"
    },
    {
      "date": "2018-02",
      "oni": -0.67,
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
        "nino34": -0.886,
        "karimata": -0.442,
        "makassar": -0.003,
        "jawa": -0.493,
        "maluku": 0.01
      },
      "split": "train"
    },
    {
      "date": "2018-03",
      "oni": -0.55,
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
        "nino34": -1.002,
        "karimata": -0.033,
        "makassar": -0.121,
        "jawa": 0.017,
        "maluku": -0.112
      },
      "split": "train"
    },
    {
      "date": "2018-04",
      "oni": -0.35,
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
      "date": "2018-05",
      "oni": -0.07,
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
      "date": "2018-06",
      "oni": 0.13,
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
      "date": "2018-07",
      "oni": 0.2,
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
        "nino34": 0.151,
        "karimata": -0.704,
        "makassar": -0.356,
        "jawa": -1.344,
        "maluku": -0.173
      },
      "split": "train"
    },
    {
      "date": "2018-08",
      "oni": 0.3,
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
        "nino34": 0.367,
        "karimata": -0.428,
        "makassar": -0.342,
        "jawa": -0.923,
        "maluku": -0.169
      },
      "split": "train"
    },
    {
      "date": "2018-09",
      "oni": 0.52,
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
        "nino34": 0.449,
        "karimata": -0.49,
        "makassar": -0.547,
        "jawa": -0.938,
        "maluku": -0.394
      },
      "split": "train"
    },
    {
      "date": "2018-10",
      "oni": 0.82,
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
        "nino34": 1.02,
        "karimata": -0.299,
        "makassar": -0.231,
        "jawa": -0.612,
        "maluku": -0.372
      },
      "split": "train"
    },
    {
      "date": "2018-11",
      "oni": 1.04,
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
        "nino34": 1.053,
        "karimata": -0.078,
        "makassar": -0.368,
        "jawa": -0.452,
        "maluku": -0.456
      },
      "split": "train"
    },
    {
      "date": "2018-12",
      "oni": 1.05,
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
        "nino34": 1.081,
        "karimata": 0.168,
        "makassar": -0.323,
        "jawa": -0.38,
        "maluku": -0.356
      },
      "split": "train"
    },
    {
      "date": "2019-01",
      "oni": 0.99,
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
        "nino34": 0.537,
        "karimata": 0.419,
        "makassar": -0.079,
        "jawa": -0.194,
        "maluku": -0.474
      },
      "split": "train"
    },
    {
      "date": "2019-02",
      "oni": 0.94,
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
        "nino34": 0.529,
        "karimata": 0.334,
        "makassar": -0.303,
        "jawa": -0.277,
        "maluku": -0.707
      },
      "split": "train"
    },
    {
      "date": "2019-03",
      "oni": 0.87,
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
        "nino34": 0.757,
        "karimata": 0.43,
        "makassar": -0.519,
        "jawa": -0.222,
        "maluku": -0.664
      },
      "split": "train"
    },
    {
      "date": "2019-04",
      "oni": 0.82,
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
      "date": "2019-05",
      "oni": 0.71,
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
      "date": "2019-06",
      "oni": 0.59,
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
      "date": "2019-07",
      "oni": 0.38,
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
        "nino34": 0.347,
        "karimata": -0.444,
        "makassar": -0.551,
        "jawa": -1.364,
        "maluku": -0.672
      },
      "split": "train"
    },
    {
      "date": "2019-08",
      "oni": 0.2,
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
        "nino34": 0.228,
        "karimata": -0.726,
        "makassar": -0.733,
        "jawa": -1.186,
        "maluku": -0.69
      },
      "split": "train"
    },
    {
      "date": "2019-09",
      "oni": 0.31,
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
        "nino34": 0.093,
        "karimata": -0.741,
        "makassar": -0.615,
        "jawa": -0.978,
        "maluku": -0.724
      },
      "split": "train"
    },
    {
      "date": "2019-10",
      "oni": 0.51,
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
        "nino34": 0.665,
        "karimata": -0.218,
        "makassar": -0.08,
        "jawa": -0.611,
        "maluku": -0.367
      },
      "split": "train"
    },
    {
      "date": "2019-11",
      "oni": 0.72,
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
        "nino34": 0.635,
        "karimata": 0.193,
        "makassar": -0.065,
        "jawa": -0.632,
        "maluku": -0.351
      },
      "split": "train"
    },
    {
      "date": "2019-12",
      "oni": 0.75,
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
        "nino34": 0.591,
        "karimata": -0.161,
        "makassar": 0.174,
        "jawa": 0.694,
        "maluku": -0.114
      },
      "split": "train"
    },
    {
      "date": "2020-01",
      "oni": 0.71,
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
        "nino34": 0.381,
        "karimata": -0.338,
        "makassar": 0.025,
        "jawa": 0.413,
        "maluku": -0.112
      },
      "split": "train"
    },
    {
      "date": "2020-02",
      "oni": 0.66,
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
        "nino34": 0.162,
        "karimata": 0.188,
        "makassar": -0.001,
        "jawa": 0.723,
        "maluku": -0.008
      },
      "split": "train"
    },
    {
      "date": "2020-03",
      "oni": 0.57,
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
        "nino34": 0.238,
        "karimata": 0.306,
        "makassar": 0.006,
        "jawa": 0.27,
        "maluku": 0.039
      },
      "split": "train"
    },
    {
      "date": "2020-04",
      "oni": 0.33,
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
      "date": "2020-05",
      "oni": 0.04,
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
      "date": "2020-06",
      "oni": -0.18,
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
      "date": "2020-07",
      "oni": -0.29,
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
        "nino34": -0.236,
        "karimata": 0.057,
        "makassar": 0.124,
        "jawa": 0.159,
        "maluku": 0.384
      },
      "split": "train"
    },
    {
      "date": "2020-08",
      "oni": -0.43,
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
        "nino34": -0.47,
        "karimata": 0.436,
        "makassar": 0.284,
        "jawa": 0.254,
        "maluku": 0.335
      },
      "split": "train"
    },
    {
      "date": "2020-09",
      "oni": -0.77,
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
        "nino34": -0.552,
        "karimata": 0.044,
        "makassar": 0.085,
        "jawa": 0.121,
        "maluku": 0.315
      },
      "split": "train"
    },
    {
      "date": "2020-10",
      "oni": -1.0,
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
        "nino34": -1.025,
        "karimata": -0.222,
        "makassar": 0.123,
        "jawa": -0.23,
        "maluku": 0.342
      },
      "split": "train"
    },
    {
      "date": "2020-11",
      "oni": -1.11,
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
        "nino34": -1.081,
        "karimata": -0.404,
        "makassar": -0.083,
        "jawa": 0.088,
        "maluku": 0.241
      },
      "split": "train"
    },
    {
      "date": "2020-12",
      "oni": -1.06,
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
        "nino34": -0.843,
        "karimata": -0.329,
        "makassar": -0.16,
        "jawa": 0.117,
        "maluku": 0.239
      },
      "split": "train"
    },
    {
      "date": "2021-01",
      "oni": -0.99,
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
        "nino34": -1.06,
        "karimata": -0.848,
        "makassar": -0.391,
        "jawa": -0.435,
        "maluku": 0.495
      },
      "split": "train"
    },
    {
      "date": "2021-02",
      "oni": -0.85,
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
        "nino34": -1.07,
        "karimata": -0.881,
        "makassar": 0.065,
        "jawa": -0.415,
        "maluku": 0.594
      },
      "split": "train"
    },
    {
      "date": "2021-03",
      "oni": -0.74,
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
        "nino34": -0.803,
        "karimata": -0.313,
        "makassar": 0.089,
        "jawa": -0.358,
        "maluku": 0.331
      },
      "split": "train"
    },
    {
      "date": "2021-04",
      "oni": -0.56,
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
      "date": "2021-05",
      "oni": -0.4,
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
      "date": "2021-06",
      "oni": -0.31,
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
      "date": "2021-07",
      "oni": -0.35,
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
        "nino34": -0.273,
        "karimata": 0.036,
        "makassar": -0.004,
        "jawa": 0.609,
        "maluku": 0.034
      },
      "split": "train"
    },
    {
      "date": "2021-08",
      "oni": -0.46,
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
        "nino34": -0.21,
        "karimata": 0.069,
        "makassar": 0.157,
        "jawa": 0.278,
        "maluku": 0.277
      },
      "split": "train"
    },
    {
      "date": "2021-09",
      "oni": -0.64,
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
        "nino34": -0.16,
        "karimata": 0.191,
        "makassar": 0.249,
        "jawa": 0.199,
        "maluku": 0.312
      },
      "split": "train"
    },
    {
      "date": "2021-10",
      "oni": -0.77,
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
        "nino34": -0.659,
        "karimata": 0.096,
        "makassar": 0.115,
        "jawa": 0.054,
        "maluku": 0.26
      },
      "split": "train"
    },
    {
      "date": "2021-11",
      "oni": -0.91,
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
        "nino34": -0.699,
        "karimata": -0.054,
        "makassar": 0.217,
        "jawa": -0.006,
        "maluku": 0.284
      },
      "split": "train"
    },
    {
      "date": "2021-12",
      "oni": -0.83,
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
        "nino34": -0.899,
        "karimata": 0.122,
        "makassar": 0.108,
        "jawa": 0.185,
        "maluku": 0.002
      },
      "split": "train"
    },
    {
      "date": "2022-01",
      "oni": -0.76,
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
        "nino34": -0.984,
        "karimata": -0.022,
        "makassar": -0.051,
        "jawa": 0.134,
        "maluku": -0.059
      },
      "split": "val"
    },
    {
      "date": "2022-02",
      "oni": -0.68,
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
        "nino34": -0.907,
        "karimata": 0.135,
        "makassar": -0.038,
        "jawa": -0.128,
        "maluku": 0.081
      },
      "split": "val"
    },
    {
      "date": "2022-03",
      "oni": -0.77,
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
        "nino34": -1.129,
        "karimata": 0.336,
        "makassar": 0.217,
        "jawa": -0.085,
        "maluku": 0.227
      },
      "split": "val"
    },
    {
      "date": "2022-04",
      "oni": -0.86,
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
      "date": "2022-05",
      "oni": -0.83,
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
      "date": "2022-06",
      "oni": -0.73,
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
      "date": "2022-07",
      "oni": -0.7,
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
        "nino34": -0.713,
        "karimata": 0.285,
        "makassar": 0.336,
        "jawa": 0.673,
        "maluku": 0.195
      },
      "split": "val"
    },
    {
      "date": "2022-08",
      "oni": -0.78,
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
        "nino34": -0.894,
        "karimata": 0.287,
        "makassar": 0.348,
        "jawa": 0.61,
        "maluku": 0.277
      },
      "split": "val"
    },
    {
      "date": "2022-09",
      "oni": -0.87,
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
        "nino34": -0.818,
        "karimata": 0.154,
        "makassar": 0.419,
        "jawa": 0.675,
        "maluku": 0.446
      },
      "split": "val"
    },
    {
      "date": "2022-10",
      "oni": -0.89,
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
        "nino34": -0.706,
        "karimata": -0.172,
        "makassar": -0.031,
        "jawa": 0.289,
        "maluku": 0.146
      },
      "split": "val"
    },
    {
      "date": "2022-11",
      "oni": -0.82,
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
        "nino34": -0.773,
        "karimata": -0.472,
        "makassar": 0.01,
        "jawa": -0.415,
        "maluku": 0.221
      },
      "split": "val"
    },
    {
      "date": "2022-12",
      "oni": -0.7,
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
        "nino34": -0.678,
        "karimata": -0.246,
        "makassar": 0.182,
        "jawa": -0.274,
        "maluku": 0.097
      },
      "split": "val"
    },
    {
      "date": "2023-01",
      "oni": -0.55,
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
        "nino34": -0.828,
        "karimata": -0.391,
        "makassar": 0.089,
        "jawa": -0.287,
        "maluku": 0.103
      },
      "split": "val"
    },
    {
      "date": "2023-02",
      "oni": -0.33,
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
        "nino34": -0.647,
        "karimata": -0.305,
        "makassar": -0.17,
        "jawa": -0.746,
        "maluku": 0.158
      },
      "split": "val"
    },
    {
      "date": "2023-03",
      "oni": -0.11,
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
        "nino34": -0.26,
        "karimata": -0.867,
        "makassar": 0.046,
        "jawa": -0.436,
        "maluku": 0.256
      },
      "split": "val"
    },
    {
      "date": "2023-04",
      "oni": 0.19,
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
      "date": "2023-05",
      "oni": 0.46,
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
      "date": "2023-06",
      "oni": 0.73,
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
      "date": "2023-07",
      "oni": 1.0,
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
        "nino34": 0.995,
        "karimata": -0.022,
        "makassar": 0.082,
        "jawa": -0.36,
        "maluku": 0.034
      },
      "split": "val"
    },
    {
      "date": "2023-08",
      "oni": 1.25,
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
        "nino34": 1.409,
        "karimata": -0.068,
        "makassar": 0.092,
        "jawa": -0.254,
        "maluku": -0.074
      },
      "split": "val"
    },
    {
      "date": "2023-09",
      "oni": 1.5,
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
        "nino34": 1.696,
        "karimata": -0.076,
        "makassar": -0.056,
        "jawa": -0.49,
        "maluku": -0.247
      },
      "split": "val"
    },
    {
      "date": "2023-10",
      "oni": 1.74,
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
        "nino34": 1.746,
        "karimata": 0.226,
        "makassar": 0.222,
        "jawa": 0.028,
        "maluku": -0.338
      },
      "split": "val"
    },
    {
      "date": "2023-11",
      "oni": 1.9,
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
        "nino34": 2.082,
        "karimata": 0.821,
        "makassar": 0.502,
        "jawa": -0.005,
        "maluku": -0.12
      },
      "split": "val"
    },
    {
      "date": "2023-12",
      "oni": 1.99,
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
        "nino34": 2.198,
        "karimata": 0.679,
        "makassar": 0.283,
        "jawa": -0.258,
        "maluku": 0.01
      },
      "split": "val"
    },
    {
      "date": "2024-01",
      "oni": 1.84,
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
        "nino34": 1.781,
        "karimata": 0.678,
        "makassar": 0.629,
        "jawa": 0.189,
        "maluku": 0.065
      },
      "split": "test"
    },
    {
      "date": "2024-02",
      "oni": 1.53,
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
        "nino34": 1.364,
        "karimata": 0.423,
        "makassar": 0.296,
        "jawa": 0.631,
        "maluku": -0.104
      },
      "split": "test"
    },
    {
      "date": "2024-03",
      "oni": 1.18,
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
        "nino34": 0.984,
        "karimata": 0.158,
        "makassar": -0.142,
        "jawa": -0.154,
        "maluku": -0.053
      },
      "split": "test"
    },
    {
      "date": "2024-04",
      "oni": 0.77,
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
      "date": "2024-05",
      "oni": 0.43,
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
      "date": "2024-06",
      "oni": 0.18,
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
      "date": "2024-07",
      "oni": 0.06,
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
        "nino34": 0.096,
        "karimata": 0.437,
        "makassar": 0.206,
        "jawa": 0.502,
        "maluku": 0.194
      },
      "split": "test"
    },
    {
      "date": "2024-08",
      "oni": -0.04,
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
        "nino34": 0.017,
        "karimata": 0.109,
        "makassar": 0.167,
        "jawa": 0.127,
        "maluku": 0.171
      },
      "split": "test"
    },
    {
      "date": "2024-09",
      "oni": -0.12,
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
        "nino34": -0.134,
        "karimata": 0.298,
        "makassar": 0.183,
        "jawa": 0.392,
        "maluku": 0.196
      },
      "split": "test"
    },
    {
      "date": "2024-10",
      "oni": -0.19,
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
        "nino34": -0.184,
        "karimata": 0.473,
        "makassar": 0.156,
        "jawa": 0.715,
        "maluku": 0.198
      },
      "split": "test"
    },
    {
      "date": "2024-11",
      "oni": -0.29,
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
        "nino34": 0.063,
        "karimata": 0.584,
        "makassar": 0.319,
        "jawa": 0.944,
        "maluku": 0.367
      },
      "split": "test"
    },
    {
      "date": "2024-12",
      "oni": -0.43,
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
        "nino34": -0.455,
        "karimata": 0.349,
        "makassar": 0.231,
        "jawa": 0.267,
        "maluku": 0.253
      },
      "split": "test"
    },
    {
      "date": "2025-01",
      "oni": -0.46,
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
        "nino34": -0.903,
        "karimata": -0.138,
        "makassar": 0.117,
        "jawa": -0.072,
        "maluku": 0.586
      },
      "split": "test"
    },
    {
      "date": "2025-02",
      "oni": -0.22,
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
        "nino34": -0.54,
        "karimata": -0.219,
        "makassar": 0.373,
        "jawa": -0.097,
        "maluku": 0.571
      },
      "split": "test"
    },
    {
      "date": "2025-03",
      "oni": -0.08,
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
        "nino34": -0.118,
        "karimata": -0.388,
        "makassar": 0.288,
        "jawa": 0.027,
        "maluku": 0.595
      },
      "split": "test"
    },
    {
      "date": "2025-04",
      "oni": 0.02,
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
      "date": "2025-05",
      "oni": -0.04,
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
      "date": "2025-06",
      "oni": -0.02,
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
    }
  ],
  "regions": [
    {
      "id": "nino34",
      "name": "Pasifik Ni\u00f1o 3.4",
      "key": "nino34",
      "sst": 27.688,
      "anomaly": -0.119
    },
    {
      "id": "makassar",
      "name": "Selat Makassar",
      "key": "makassar",
      "sst": 29.702,
      "anomaly": 0.181
    },
    {
      "id": "karimata",
      "name": "Selat Karimata",
      "key": "karimata",
      "sst": 30.098,
      "anomaly": 0.126
    },
    {
      "id": "jawa",
      "name": "Selatan Jawa",
      "key": "jawa",
      "sst": 28.223,
      "anomaly": 0.262
    },
    {
      "id": "maluku",
      "name": "Maluku-Papua",
      "key": "maluku",
      "sst": 29.774,
      "anomaly": 0.071
    }
  ],
  "facts": {
    "counts": {
      "elNino": 32,
      "netral": 51,
      "laNina": 31
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
      "name": "Selatan Jawa",
      "anomaly": 0.262
    }
  },
  "metrics": {
    "1": {
      "horizon_months": 1,
      "window_months": 12,
      "model": "causal_lstm_lightgbm",
      "class_mapping": {
        "0": "La Nina",
        "1": "Neutral",
        "2": "El Nino"
      },
      "validation": {
        "accuracy": 0.7692307692307693,
        "balanced_accuracy": 0.7916666666666666,
        "macro_f1": 0.6682539682539682,
        "confusion_matrix": [
          [
            1,
            0,
            0
          ],
          [
            2,
            2,
            0
          ],
          [
            0,
            1,
            7
          ]
        ],
        "lstm_oni_rmse": 1.1751062499040221
      },
      "test": {
        "accuracy": 0.7142857142857143,
        "balanced_accuracy": 0.7142857142857143,
        "macro_f1": 0.4166666666666667,
        "confusion_matrix": [
          [
            0,
            0,
            0
          ],
          [
            2,
            5,
            0
          ],
          [
            0,
            0,
            0
          ]
        ],
        "lstm_oni_rmse": 0.179630472021112
      }
    },
    "3": {
      "horizon_months": 3,
      "window_months": 12,
      "model": "causal_lstm_lightgbm",
      "class_mapping": {
        "0": "La Nina",
        "1": "Neutral",
        "2": "El Nino"
      },
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
        "lstm_oni_rmse": 1.257454002958581
      },
      "test": {
        "accuracy": 1.0,
        "balanced_accuracy": 1.0,
        "macro_f1": 1.0,
        "confusion_matrix": [
          [
            0,
            0,
            0
          ],
          [
            0,
            7,
            0
          ],
          [
            0,
            0,
            0
          ]
        ],
        "lstm_oni_rmse": 0.17404725937457927
      }
    },
    "6": {
      "horizon_months": 6,
      "window_months": 12,
      "model": "causal_lstm_lightgbm",
      "class_mapping": {
        "0": "La Nina",
        "1": "Neutral",
        "2": "El Nino"
      },
      "validation": {
        "accuracy": 0.0,
        "balanced_accuracy": 0.0,
        "macro_f1": 0.0,
        "confusion_matrix": [
          [
            0,
            0,
            0
          ],
          [
            2,
            0,
            0
          ],
          [
            11,
            0,
            0
          ]
        ],
        "lstm_oni_rmse": 1.2576584167230795
      },
      "test": {
        "accuracy": 0.0,
        "balanced_accuracy": 0.0,
        "macro_f1": 0.0,
        "confusion_matrix": [
          [
            0,
            0,
            3
          ],
          [
            0,
            0,
            4
          ],
          [
            0,
            0,
            0
          ]
        ],
        "lstm_oni_rmse": 0.21745361805342941
      }
    }
  },
  "derived": {
    "1": {
      "kmrvMae": 0.172,
      "persistenceMae": 0.108,
      "samples": 7
    },
    "3": {
      "kmrvMae": 0.152,
      "persistenceMae": 0.098,
      "samples": 7
    },
    "6": {
      "kmrvMae": 0.197,
      "persistenceMae": 0.1,
      "samples": 7
    }
  },
  "testPredictions": {
    "1": [
      {
        "date": "2024-12-01",
        "actual_oni": -0.46,
        "lstm_oni": -0.344,
        "actual_phase": 1,
        "predicted_phase": 0
      },
      {
        "date": "2025-01-01",
        "actual_oni": -0.22,
        "lstm_oni": -0.372,
        "actual_phase": 1,
        "predicted_phase": 0
      },
      {
        "date": "2025-02-01",
        "actual_oni": -0.08,
        "lstm_oni": -0.266,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-03-01",
        "actual_oni": 0.02,
        "lstm_oni": -0.259,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-04-01",
        "actual_oni": -0.04,
        "lstm_oni": -0.158,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-05-01",
        "actual_oni": -0.02,
        "lstm_oni": -0.214,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-06-01",
        "actual_oni": -0.11,
        "lstm_oni": -0.27,
        "actual_phase": 1,
        "predicted_phase": 1
      }
    ],
    "3": [
      {
        "date": "2024-12-01",
        "actual_oni": -0.08,
        "lstm_oni": -0.383,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-01-01",
        "actual_oni": 0.02,
        "lstm_oni": -0.208,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-02-01",
        "actual_oni": -0.04,
        "lstm_oni": 0.057,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-03-01",
        "actual_oni": -0.02,
        "lstm_oni": 0.07,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-04-01",
        "actual_oni": -0.11,
        "lstm_oni": 0.086,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-05-01",
        "actual_oni": -0.26,
        "lstm_oni": -0.158,
        "actual_phase": 1,
        "predicted_phase": 1
      },
      {
        "date": "2025-06-01",
        "actual_oni": -0.43,
        "lstm_oni": -0.383,
        "actual_phase": 1,
        "predicted_phase": 1
      }
    ],
    "6": [
      {
        "date": "2024-12-01",
        "actual_oni": -0.02,
        "lstm_oni": -0.248,
        "actual_phase": 1,
        "predicted_phase": 2
      },
      {
        "date": "2025-01-01",
        "actual_oni": -0.11,
        "lstm_oni": -0.134,
        "actual_phase": 1,
        "predicted_phase": 2
      },
      {
        "date": "2025-02-01",
        "actual_oni": -0.26,
        "lstm_oni": -0.053,
        "actual_phase": 1,
        "predicted_phase": 2
      },
      {
        "date": "2025-03-01",
        "actual_oni": -0.43,
        "lstm_oni": -0.256,
        "actual_phase": 1,
        "predicted_phase": 2
      },
      {
        "date": "2025-04-01",
        "actual_oni": -0.57,
        "lstm_oni": -0.404,
        "actual_phase": 0,
        "predicted_phase": 2
      },
      {
        "date": "2025-05-01",
        "actual_oni": -0.61,
        "lstm_oni": -0.838,
        "actual_phase": 0,
        "predicted_phase": 2
      },
      {
        "date": "2025-06-01",
        "actual_oni": -0.6,
        "lstm_oni": -0.955,
        "actual_phase": 0,
        "predicted_phase": 2
      }
    ]
  }
};

export const meta = realData.meta;
export const latest = realData.latest;
export const history = realData.history;
export const regions = realData.regions;
export const facts = realData.facts;
export const metrics = realData.metrics;
export const derived = realData.derived;
export const testPredictions = realData.testPredictions;
