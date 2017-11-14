# coding: utf-8

import numpy as np

def editParameters(parameters, fieldDottedName, domainValue):
    fieldDottedName = fieldDottedName.strip().split(".")
    currentParameters = parameters
    started = False
    for currentName in fieldDottedName:
        if started:
            currentParameters = currentParameters['subparams']
        started = True
        for current in currentParameters:
            if current['name'] == currentName:
                currentParameters = current
                break
    currentParameters["force"] = domainValue

def getDomain(parameters, fieldDottedName):
    fieldDottedName = fieldDottedName.strip().split(".")
    currentParameters = parameters
    started = False
    for currentName in fieldDottedName:
        if started:
            currentParameters = currentParameters['subparams']
        started = True
        found = False
        for current in currentParameters:
            if current['name'] == currentName:
                currentParameters = current
                found = True
                break
        if not found:
            return None
    if "force" in currentParameters:
        return currentParameters["force"]
    else:
        return currentParameters["domain"]

###############################################################################
############################### bestCombsDef ##################################
###############################################################################

# The only one which is fully updated :
bestCombsDef = \
[
    {
        'name': 'score',
        'domain': ['MeanLeastSquares', 'MeanDifference', 'ScipyPearsonCorrelation', 'NumpyPearsonCorrelation', 'AgirrePearsonCorrelation'],
        'force': ['NumpyPearsonCorrelation']
    },
    {
        'name': 'regressor',
        'domain': ['KernelRidge', 'LinearRegression', 'Ridge', 'RidgeCV', 'Lasso', 'ElasticNet', 'LinearSVR', 'SVR', 'NuSVR'],
        'force': ['RidgeCV'],
        # 'force': ['LinearSVR', 'SVR', 'NuSVR'],
        'subparams':
        [
            {
                'constraints': [['Ridge', 'RidgeCV', 'Lasso', 'ElasticNet', 'KernelRidge']],
                'name': 'alpha',
                'domain': np.arange(0.1, 3.0, 0.1),
                'force': [1.0] # 1.0 or 2.7
            },
            {
                'constraints': [['ElasticNet']],
                'name': 'l1_ratio',
                'domain': np.arange(0.0, 1.0, 0.1),
                'force': [0.5]
            },
            {
                'constraints': [['SVR', 'LinearSVR']],
                'name': 'epsilon',
                'domain': [0.03, 0.06, 0.1, 0.13, 0.16, 0.2],
                'force': [0.1]
            },
            {
                'constraints': [['NuSVR']],
                'name': 'nu',
                'domain': np.arange(0.1, 1.0, 0.1),
                'force': [0.5]
            },
            {
                'constraints': [['SVR', 'NuSVR', 'LinearSVR']],
                'name': 'C',
                'domain': [0.1, 0.5, 1.0, 1.5, 2.0],
                'force': [1.0]
            },
            {
                'constraints': [['SVR', 'NuSVR']],
                'name': 'shrinking',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [['LinearSVR']],
                'name': 'dual',
                'domain': [True, False],
                'force': [False]
            },
            {
                'constraints': [['SVR', 'NuSVR', 'KernelRidge']],
                'name': 'kernel',
                'domain': ['linear', 'poly', 'rbf', 'sigmoid', 'precomputed'],
                'force': ['rbf'],
                'subparams':
                [
                    {
                        'constraints': [['poly']],
                        'name': 'degree',
                        'domain': [1, 2, 3, 4, 5, 6],
                        'force': [3]
                    },
                    {
                        'constraints': [['poly', 'rbf', 'sigmoid']],
                        'name': 'gamma',
                        'domain': [0.03, 0.06, 0.1, 0.13, 0.16, 0.2],
                        'force': [0.1]
                    },
                    {
                        'constraints': [['poly', 'sigmoid']],
                        'name': 'coef0',
                        'domain': np.arange(0.0, 1.0, 0.1),
                        'force': [0.0]
                    }
                ]
            }
        ]
    },
    {
        'name': 'data',
        'domain': ['DLSMappingSets2015', 'SamsungPolandMappingSets2016', 'NormalSets2016', 'NormalSets2015', 'Normal2012', 'Normal2015', 'Normal2016', 'CrossValidation2015', 'CrossValidation2016', 'CrossValidation2017', 'FeatureAnalysis2016'],
        'disabled': False,
#         'force': ['CrossValidation2016', 'Normal2016'],
#         'force': ['DLSMappingSets2015'],
#         'force': ['NormalSets2016'],
        'force': ['SamsungPolandMappingSets2016'],
#         'force': ['FeatureAnalysis2016'],
        #'force': ['CrossValidation2017'],
#         'force': ['CrossValidation2016'],
        'subparams':
        [
            {
                'constraints': [['CrossValidation2015', 'CrossValidation2016', 'CrossValidation2017']],
                'name': 'partsCount',
                'domain': [3, 5, 10, 20],
                'force': [10]
            },
            {
                'constraints': [['NormalSets2016', 'NormalSets2015', 'SamsungPolandMappingSets2016']],
                'name': 'paperPairsCount',
                'domain': [True, False],
                'force': [False]
            },
            {
                'constraints': [['SamsungPolandMappingSets2016']],
                'name': 'featureAnalysis',
                'domain': [True, False],
                'force': [False]
            },
            {
                'name': 'addSMT2013',
                'domain': [True, False],
                'force': [True]
            }
        ]
    },
    {
        'name': 'agParser',
        'domain': [True],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'removeStopWords',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [[True]],
                'name': 'removePunct',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [[True]],
                'name': 'toLowerCase',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [[True]],
                'name': 'lemma',
                'domain': [True, False],
                'force': [False]
            }
        ]
    },
    {
        'name': 'BaroniVectorsFeature',
        'domain': [True, False],
        'force': [True],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'cosinusNSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0],
                        'force': [0.0]
                    },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False]
            },
            {
                'constraints': [[True]],
                'name': 'centroid',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [[True]],
                'name': 'max',
                'domain': [True, False],
                'force': [True] # True pour cv2016
            },
            {
                'constraints': [[True]],
                'name': 'parsingConfigs',
                'domain': [[None]],
                'force':
                [
                    [ # best 2016
                        "_lemma_nopunct_lowercase_isDLS2015SwOrPunct1",
                        "_lemma_nopunct_lowercase_smallsw1",
                        "_lemma_nopunct_lowercase_bigsw1",
                        "_nopunct_lowercase_isDLS2015SwOrPunct1",
                        "_nopunct_lowercase_smallsw1",
                        "_nopunct_lowercase_bigsw1",
                        "_lemma_nopunct_lowercase",
                        "_nopunct_lowercase",
                    ],
#                     [
#                         "_nopunct_lemma_lowercase_isDLS2015SwOrPunct1",
#                         "_lemma_nopunct_lowercase_bigsw1",
#                         "_nopunct_lemma_lowercase",
#                     ],
#                     [ # Official
#                         "_lemma_lowercase_isDLS2015SwOrPunct1",
#                     ],
#                     [
#                         "_lowercase_isDLS2015SwOrPunct1",
#                     ],
#                     [ # best 2015
#                         "_nopunct_lemma_lowercase_isDLS2015SwOrPunct1",
#                         "_lemma_nopunct_lowercase_bigsw1",
#                         "_nopunct_lemma_lowercase",
#                         "_lemma_lowercase_isDLS2015SwOrPunct1",
#                         "_lemma_lowercase_bigsw1",
#                         "_lemma_lowercase",
#                     ],
                ],
            },
        ]
    },
    {
        'name': 'LengthFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [False],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'string',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [[True]],
                'name': 'tokens',
                'domain': [True, False],
                'force': [False] # False for best dls2015
            }
        ]
    },
    {
        'name': 'JacanaAlignFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [True],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'parsingConfigs',
                'domain': [[None]],
                'force':
                [
                    [ # best for cv2016
                        "_nostopword_nopunct_lowercase_smallsw1",
                        "_nostopword_nopunct_lowercase_bigsw1",
                        "_nostopword_nopunct_lemma_lowercase_smallsw1",
                        "_nostopword_nopunct_lemma_lowercase_bigsw1",
                        "_nopunct_lemma_lowercase",
                        "_nopunct_lowercase",
                    ],
#                     [
#                         "_nostopword_nopunct_lowercase_smallsw3",
#                         "_nostopword_nopunct_lowercase_bigsw1",
#                         "_nostopword_nopunct_lemma_lowercase_smallsw3",
#                         "_nostopword_nopunct_lemma_lowercase_bigsw1",
#                         "_nopunct_lemma_lowercase",
#                         "_nopunct_lowercase",
#                     ],
#                     [
#                         "_nostopword_nopunct_lowercase_smallsw1",
#                         "_nostopword_nopunct_lowercase_bigsw1",
#                         "_nopunct_lemma_lowercase",
#                     ],
#                     [
#                         "_nostopword_nopunct_lowercase_smallsw1",
#                     ],
#                     [
#                         "_nostopword_nopunct_lowercase_smallsw1",
#                         "_nostopword_nopunct_lowercase_nltlsw",
#                         "_nostopword_nopunct_lowercase_bigsw1",
#                     ],
                 ]
            },
            {
                'constraints': [[True]],
                'name': 'defaultScore',
                'domain': [0.0, 0.5, 1.0],
                'force': [1.0] # 1.0 best cv2016
            },
        ]
    },
    {
        'name': 'SentencePairFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [True],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'sameUpperCaseCount',
                'domain': [True, False],
                'force': [False]
            },
            {
                'constraints': [[True]],
                'name': 'sameLemmaCount',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [[True]],
                'name': 'nGramOverlap',
                'domain': [True, False],
                'force': [False],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': '2gram', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': '3gram', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': '4gram', 'domain': [True, False], 'force': [False] },
                    { 'constraints': [[True]], 'name': '5gram', 'domain': [True, False], 'force': [False] },
                    { 'constraints': [[True]], 'name': 'lemmaWithSw', 'domain': [True, False], 'force': [False] },
                    { 'constraints': [[True]], 'name': 'lemma', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'word', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'wordWithSw', 'domain': [True, False], 'force': [False] },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'word',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'stringLength', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'substraction', 'domain': [True, False], 'force': [True] },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'punct',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'stopword',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'smallsw3', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'bigsw1', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'nltksw', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'swTokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'stringLength', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'substraction', 'domain': [True, False], 'force': [True] },
                ]
            },
        ]
    },
    {
        'name': 'SultanAlignerFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [True],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'similarity1',
                'domain': [True, False],
                'force': [False],
            },
            {
                'constraints': [[True]],
                'name': 'similarity2',
                'domain': [True, False],
                'force': [True], # To add for 2016
            },
            {
                'constraints': [[True]],
                'name': 'similarity3', # BEST
                'domain': [True, False],
                'force': [True],
            },
            {
                'constraints': [[True]],
                'name': 'targetedAlignment',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'namedEntities',
                        'domain': [True, False],
                        'force': [True],
                        'subparams':
                        [
                            {
                                'constraints': [[True]],
                                'name': 'type',
                                'domain': ["average", "ratios", "total"],
                                'force': ["total"],
                            },
                            {
                                'constraints': [[True]],
                                'name': 'tagList',
                                'domain': [[u'MISC', u'ORGANIZATION', u'NUMBER', u'PERSON', u'LOCATION', u'SET', u'DATE', u'DURATION', u'MONEY', u'ORDINAL', u'TIME', u'PERCENT']],
                                'force':
                                [
#                                     [u'ORGANIZATION', u'NUMBER', u'PERSON', u'LOCATION', u'DATE', u'DURATION', u'MONEY', u'ORDINAL', u'TIME', u'PERCENT'],
                                    [u'MISC', u'ORGANIZATION', u'NUMBER', u'PERSON', u'LOCATION', u'SET', u'DATE', u'DURATION', u'MONEY', u'ORDINAL', u'TIME', u'PERCENT'],
#                                     [u'MISC', u'ORGANIZATION', u'NUMBER', u'PERSON', u'LOCATION', u'SET', u'MONEY', u'ORDINAL', u'PERCENT'],
#                                     [u'MISC', u'ORGANIZATION', u'NUMBER', u'PERSON', u'LOCATION', u'DATE', u'DURATION', u'TIME'],
#                                     [u'MISC', u'ORGANIZATION', u'PERSON', u'LOCATION'],
#                                     [u'ORGANIZATION', u'PERSON', u'LOCATION'],
#                                     [u'NUMBER', u'DATE', u'DURATION', u'MONEY', u'ORDINAL', u'TIME', u'PERCENT'],
                                ],
                            },
                         
                        ]
                    },
                    {
                        'constraints': [[True]],
                        'name': 'verbs',
                        'domain': [True, False],
                        'force': [False],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'defaultScore',
                        'domain': [0.0, 0.5, 1.0],
                        'force': [1.0],
                    },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'parsingConfigs',
                'domain': [[None]],
                'force':
                [
#                     [ # BEST for 2015
#                         "isDLS2015SwOrPunct1"
#                     ],

                    [ # BEST for 2016
                        "_smallsw1",
                        "_bigsw1",
                        "isDLS2015SwOrPunct1"
                    ],
# 
# 
#                     [
#                         "_smallsw3",
#                         "_bigsw1",
#                         "isDLS2015SwOrPunct1"
#                     ],
#                     [
#                         "_bigsw1",
#                         "isDLS2015SwOrPunct1"
#                     ],
#                     [
#                         "_smallsw3"
#                     ],
#                     [
#                         "_smallsw1"
#                     ],
#                     [
#                         "_smallsw1",
#                         "isDLS2015SwOrPunct1"
#                     ],
#                     [
#                         "isDLS2015SwOrPunct1"
#                         "sentsw"
#                     ],
#                     [
#                         "isDLS2015SwOrPunct2"
#                     ],
                ],
            },
        ]
    },
    {
        'name': 'Word2VecFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [True],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'homeMadeSimilarity',
                'domain': [True, False],
                'force': [False],
            },
            {
                'constraints': [[True]],
                'name': 'w2vNSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0], # best 0.0 pour brown_stsall et 1.0 pour GoogleNews
                        'force': [0.0]
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            },
            {
                'constraints': [[True]],
                'name': 'data',
                'domain': ['brown_stsall', 'brown', 'stsall', 'GoogleNews'],
                'force': ['GoogleNews'], # best GoogleNews then brown_stsall
                'subparams':
                [
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'min_count',
                        'sorted': True,
                        'domain': [0, 1, 3, 7, 15, 200],
                        # 'force': [5, 15]
                        'force': [0]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'window',
                        'sorted': True,
                        'domain': [1, 2, 3, 4, 5, 6, 7, 8],
                        'force': [3, 8]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'size',
                        'sorted': True,
                        'domain': [50, 100, 500, 3000],
                        'force': [100, 3000]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall', 'GoogleNews']],
                        'name': 'removeStopWords',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall', 'GoogleNews']],
                        'name': 'removePunct',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall', 'GoogleNews']],
                        'name': 'toLowerCase',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall', 'GoogleNews']],
                        'name': 'lemma',
                        'domain': [True, False],
                        'force': [False]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'dataPart',
                        'sorted': True,
                        'domain': [0.1, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0],
                        'force': [1.0]
                    },
                ]
            }
        ]
    },
    {
        'name': 'RandomFeature',
        'domain': [True, False],
        'disabled': True,
        'force': [False]
    },
    {
        'name': 'MultiDoc2VecFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [True],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'd2vSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0],
                        # 'force': [0.0, 0.5, 1.0],
                        'force': [0.0],
                        
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'firstFileIdCount',
                        'domain': [1, 2, 3, 4, 5, 6, 7, 8],
                        'force': [3],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'substraction',
                        'domain': [True, False],
                        'force': [False],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'full',
                        'domain': [True, False],
                        'force': [True],
                    },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'fileIdSet',
                'domain': [[]],
                'force': [[
#                     "_s100_w2_mc0_a0.08_i22_sa6.8e-05_lemma_nostopword_lowercase_brown",
#                     "_s100_w3_mc0_a0.08_i22_sa0.00012_lemma_nostopword_nopunct_lowercase_brown_part0.75",
#                     "_s150_w3_mc0_a0.08_i22_sa6.8e-05_lemma_nostopword_nopunct_lowercase_brown",
#                     "_s100_w3_mc0_a0.07_i22_sa0.0001_lemma_nostopword_lowercase_brown_part0.75",
#                     "_s120_w2_mc0_a0.08_i22_sa0.0001_lemma_nostopword_lowercase_stsall",
#                     "_s100_w1_mc0_a0.08_i22_sa0.0001_lemma_nostopword_nopunct_lowercase_stsall",
#                     "_s100_w2_mc0_a0.1_i10_lemma_nostopword_nopunct_lowercase_brown_part0.5",
#                     "_s100_w3_mc0_a0.12_i10_lemma_nostopword_lowercase_brown_part0.5",
#                     "_s100_w2_mc0_a0.12_i10_lemma_nostopword_nopunct_lowercase_brown_part4e-05",
#                     "_s100_w3_mc0_a0.12_i10_lemma_nostopword_lowercase_brown_part4e-05",
#                     "_s80_w3_mc0_a0.08_i22_sa0.0001_nostopword_nopunct_lowercase_brown_part0.75",
#                     "_s80_w3_mc0_a0.07_i22_sa6e-05_nostopword_lowercase_brown",
#                     "_s120_w2_mc0_a0.08_i22_sa6e-05_lemma_nostopword_nopunct_brown_part0.75",
#                     "_s120_w2_mc0_a0.07_i22_sa6e-05_lemma_nostopword_brown_part0.75",
#                     "_s100_w3_mc0_a0.08_i22_sa6e-05_nostopword_brown_part0.75",
#                     "_s100_w1_mc0_a0.07_i22_sa6e-05_lemma_nostopword_lowercase_brown",
#                     "_s150_w3_mc0_a0.07_i22_sa6e-05_lemma_nostopword_lowercase_brown",
#                     "_s150_w2_mc0_a0.07_i22_sa6e-05_lemma_nostopword_lowercase_brown",
#                     "_s120_w2_mc0_a0.08_i22_sa0.0001_lemma_nostopword_nopunct_lowercase_brown_part0.75",
#                     "_s120_w3_mc0_a0.07_i22_sa0.0001_lemma_nostopword_nopunct_lowercase_brown_part0.75",
#                     "_s80_w3_mc0_a0.07_i22_sa6e-05_lemma_nostopword_lowercase_brown",
#                     "_s80_w2_mc0_a0.1_i22_sa0.0001_lemma_nostopword_nopunct_lowercase_brown_part0.75",
#                     "_s150_w1_mc0_a0.07_i22_sa6e-05_lemma_nostopword_lowercase_brown",
#                     "_s200_w2_mc0_a0.08_i22_sa6.8e-05_lemma_nostopword_lowercase_brown",
#                     "_s100_w5_mc0_a0.08_i22_sa6.8e-05_lemma_nostopword_lowercase_brown",
#                     "_s80_w1_mc0_a0.08_i22_sa0.0001_lemma_nostopword_nopunct_lowercase_brown_part0.75",
#                     "_s200_w3_mc0_a0.08_i22_sa6.8e-05_lemma_nostopword_nopunct_lowercase_brown",
#                     "_s120_w1_mc0_a0.08_i22_sa0.0001_lemma_nostopword_nopunct_lowercase_brown_part0.75",
#                     "_s250_w2_mc0_a0.08_i22_sa6.8e-05_lemma_nostopword_nopunct_lowercase_brown",
#                     "_s150_w5_mc0_a0.07_i22_sa6e-05_lemma_nostopword_lowercase_brown",
#                     "_s250_w3_mc0_a0.08_i22_sa6.8e-05_lemma_nostopword_lowercase_brown",
#                     "_s80_w5_mc0_a0.08_i22_sa0.0001_lemma_nostopword_nopunct_lowercase_brown_part0.75",
#                     "_s200_w1_mc0_a0.08_i22_sa6.8e-05_lemma_nostopword_nopunct_lowercase_brown",
#                     "_s250_w1_mc0_a0.08_i22_sa6.8e-05_lemma_nostopword_nopunct_lowercase_brown",
#                     "_s3000_w1_mc0_a0.08_i22_sa8e-05_lemma_nostopword_nopunct_lowercase_brown_part0.75",
#                     "_s120_w5_mc0_a0.07_i22_sa0.0001_lemma_nostopword_nopunct_lowercase_brown_part0.75",
#                     "_s350_w2_mc0_a0.08_i22_sa6.8e-05_lemma_nostopword_lowercase_brown",
#                     "_s3000_w2_mc0_a0.06_i22_sa6e-05_lemma_nostopword_nopunct_lowercase_brown_part0.75",
#                     "_s500_w2_mc0_a0.07_i22_sa6e-05_lemma_nostopword_nopunct_lowercase_brown",
#                     "_s450_w1_mc0_a0.08_i22_sa6.8e-05_lemma_nostopword_nopunct_lowercase_brown",
#                     "_s500_w1_mc0_a0.07_i22_sa0.0001_lemma_nostopword_nopunct_lowercase_brown_part0.75",
#                     "_s350_w1_mc0_a0.08_i22_sa6.8e-05_lemma_nostopword_lowercase_brown",
#                     "_s3000_w3_mc0_a0.07_i22_sa0.0001_lemma_nostopword_nopunct_lowercase_brown_part0.75",
#                     "_s550_w1_mc0_a0.08_i22_sa6.8e-05_lemma_nostopword_lowercase_brown"
                ]],
            },
            {
                'constraints': [[True]],
                'name': 'bestTopDelta',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'interval',
                        'domain': [(0, 1), (2, 4)],
#                         'force': [(48, 52), (68, 75), (100, 110)],
                        'force': [(68, 72)],
                    },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'fileIdAddOn',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'first',
                        'domain': [[]],
                        'force':
                        [
                            [
                                "_s100_w2_mc0_a0.08_i22_sa6.8e-05_lemma_lowercase_smallsw1_enwiki2_part0.02",
                                "_s150_w2_mc0_a0.07_i22_sa6.8e-05_lemma_nopunct_lowercase_enwiki2_part0.02",
                                "_s100_w3_mc0_a0.08_i22_sa0.00012_lemma_nopunct_lowercase_smallsw1_enwiki2_part0.02",
                                "_s1000_w1_mc0_a0.07_i22_sa6e-05_lemma_nopunct_lowercase_enwiki2_part0.02",
                                "_s4000_w20_mc0_a0.12_i10_sa1e-05_lemma_nopunct_lowercase_enwiki2_part0.02",
                                "_s1184_w1_mc6_a0.13_i18_sa4.68e-05_n2_lemma_lowercase_enwiki2_part0.02",
                                "_s200_w1_mc0_a0.07_i22_sa6e-05_lemma_lowercase_enwiki2_part0.02",
                                "_s1326_w1_mc3_a0.1_i14_sa0.0001452_lemma_nopunct_lowercase_enwiki2_part0.02",
                                "_s3000_w8_mc200_a0.1_i20_n5_lemma_nopunct_lowercase_enwiki2_part0.02",
                                "_s5176_w5_mc145_a0.06_i20_sa5.66e-05_n7_nopunct_smallsw1_enwiki2_part0.02",
                                "_s100_w2_mc0_a0.1_i22_n29_lemma_nopunct_lowercase_enwiki2_part0.02",
                                "_s150_w1_mc0_a0.07_i22_sa6e-05_n200_lemma_nopunct_lowercase_enwiki2_part0.02",

#                                     "_s5797_w1_mc10_a0.1_i13_sa5.53e-05_n10_nopunct_lowercase_brown_part0.9",
#                                     "_s4000_w20_mc0_a0.12_i10_sa1e-05_lemma_nopunct_lowercase_brown_part0.5",

#                                 "_s150_w2_mc0_a0.07_i22_sa6.8e-05_lemma_nopunct_lowercase_brown"

#                                 "_s300_w8_mc0_a0.025_i5_sa0_lemma_lowercase_brown"
                            ]
                        ],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'end',
                        'domain': [[]],
                        'force': [[]],
                    },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'topdelta',
                'domain': [True, False],
                'force': [False],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'alpha',
                        'domain': [0.2, 0.9],
                        'force': [0.9],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'beta',
                        'domain': [0.2, 1.0],
                        'force': [0.4],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'sigma',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0],
                        'force': [0.2],
#                         'force': [0.8],
#                         'force': [0.5],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'omegas',
                        'domain': [[1.0], [0.7, 0.25, 0.05], [0.5, 0.4, 0.3, 0.1]],
                        #'force': [[0.7, 0.25, 0.05]],
                        'force': [[1.0]],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'beginTopCount',
                        'domain': [0, 1, 2, 3, 4, 5],
                        'force': [1],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'beginByTopdef',
                        'domain': [False],
                        'force': [True],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'fusionSchedule',
                        'domain': [[1, 1], [3, 1], [1, 3], [1, 1, 2, 1], [1, 2], [2, 1], [1, 2, 1, 1]],
#                         'force': [[1, 1, 2, 1], [1, 1], [1, 2, 1, 1]],
#                         'force': [[1, 1, 2, 1]],
#                         'force': [[1, 1]],
#                         'force': [[1, 2, 1, 1]],
#                         'force': [[3, 1]],
                        'force': [[1, 3]],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'infBoundScore',
                        'domain': [0.0, 0.4, 0.7],
                        'force': [0.0],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'maxCount',
                        'domain': [104],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'maxTopDelta',
#                         'domain': range(1, 154, 4),
                        'domain': range(1, 301, 1),
                    },
                ]
            }
        ]
    },
    {
        'name': 'Doc2VecFeature',
        'domain': [True, False],
        'disabled': True,
        'force': [False],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'data',
                'domain': ['ukwac', 'enwiki', 'ukwac_enwiki', 'halfukwac', 'brown', 'stsall'],
                # 'force': ['brown', 'stsall'],
                # 'force': ['ukwac'],
                'force': ['brown'],
                'subparams':
                [
                    {
                        'name': 'sample',
                        'sorted': True,
                        'default': 0.0,
                        'domain': [0.0, 1e-5],
                        # 'force': np.arange(0.00034, 0.00037, 0.000001)
                        'force': [0.0]
                    },
                    {
                        'name': 'iter',
                        'sorted': True,
                        'default': 5,
                        'domain': range(1, 20, 1),
                        'force': [22]
                    },
                    {
                        'name': 'negative',
                        'sorted': True,
                        'default': 0,
                        'domain': range(5, 20, 1),
                        'force': [0]
                    },
                    {
                        'name': 'alpha',
                        'default': 0.025,
                        'sorted': True,
                        'domain': [0.005, 0.010, 0.015, 0.020, 0.025, 0.030, 0.035, 0.040, 0.045],
                        # 'force': [5, 15]
#                         'force': [0.045, 0.7, 0.8, 0.9, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.2, 0.3, 0.4, 0.5]
#                         'force': [0.045, 0.1, 0.2, 0.3, 0.4, 0.5]
#                         'force': np.arange(0.07, 0.15, 0.01)
                        'force': [0.1]
                    },
                    {
                        'name': 'min_count',
                        'sorted': True,
                        'domain': [0, 1, 3, 7, 15, 200],
                        # 'force': [5, 15]
                        'force': [0]
                    },
                    {
                        'name': 'window',
                        'sorted': True,
                        'domain': [2, 3, 8],
                        # 'force': [1, 2, 3, 8]
                        # 'force': [1, 2, 3, 4, 5, 6, 7, 8]
                    },
                    {
                        'name': 'size',
                        'sorted': True,
                        'domain': [50, 100, 500, 3000],
                        'force': [10, 50, 100, 120, 140, 160, 180, 200, 250, 300, 400, 500, 600, 800, 1000, 1200, 1500, 2000, 2500, 3000, 4000, 4400, 5000, 6000, 7000]
                    },
                    {
                        'name': 'removeStopWords',
                        'domain': [True, False],
                        'force': [False]
                    },
                    {
                        'name': 'removePunct',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'name': 'toLowerCase',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'name': 'lemma',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'name': 'dataPart',
                        'sorted': True,
                        'domain': [0.1, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0],
                        # 'force': [0.0, 0.25, 0.5, 0.75, 1.0]
                        # 'force': [0.0, 0.5, 1.0]
                        # 'force': [0.0, 1.0]
                        # 'force': [0.0, 0.5, 1.0]
                        'force': [0.75]
                    },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'd2vSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0],
                        # 'force': [0.0, 0.5, 1.0],
                        'force': [0.0],
                        
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            }
        ]
    }
]

###############################################################################
############################### d2vVsW2vCombsDef ##################################
###############################################################################

# The only one which is fully updated :
d2vVsW2vCombsDef = \
[
    {
        'name': 'score',
        'domain': ['MeanLeastSquares', 'MeanDifference', 'ScipyPearsonCorrelation', 'NumpyPearsonCorrelation', 'AgirrePearsonCorrelation'],
        'force': ['NumpyPearsonCorrelation']
    },
    {
        'name': 'regressor',
        'domain': ['KernelRidge', 'LinearRegression', 'Ridge', 'RidgeCV', 'Lasso', 'ElasticNet', 'LinearSVR', 'SVR', 'NuSVR'],
        'force': ['Ridge'],
        # 'force': ['LinearSVR', 'SVR', 'NuSVR'],
        'subparams':
        [
            {
                'constraints': [['Ridge', 'RidgeCV', 'Lasso', 'ElasticNet', 'KernelRidge']],
                'name': 'alpha',
                'domain': np.arange(0.1, 3.0, 0.1),
                'force': [2.7]
            },
            {
                'constraints': [['ElasticNet']],
                'name': 'l1_ratio',
                'domain': np.arange(0.0, 1.0, 0.1),
                'force': [0.5]
            },
            {
                'constraints': [['SVR', 'LinearSVR']],
                'name': 'epsilon',
                'domain': [0.03, 0.06, 0.1, 0.13, 0.16, 0.2],
                'force': [0.1]
            },
            {
                'constraints': [['NuSVR']],
                'name': 'nu',
                'domain': np.arange(0.1, 1.0, 0.1),
                'force': [0.5]
            },
            {
                'constraints': [['SVR', 'NuSVR', 'LinearSVR']],
                'name': 'C',
                'domain': [0.1, 0.5, 1.0, 1.5, 2.0],
                'force': [1.0]
            },
            {
                'constraints': [['SVR', 'NuSVR']],
                'name': 'shrinking',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [['LinearSVR']],
                'name': 'dual',
                'domain': [True, False],
                'force': [False]
            },
            {
                'constraints': [['SVR', 'NuSVR', 'KernelRidge']],
                'name': 'kernel',
                'domain': ['linear', 'poly', 'rbf', 'sigmoid', 'precomputed'],
                'force': ['rbf'],
                'subparams':
                [
                    {
                        'constraints': [['poly']],
                        'name': 'degree',
                        'domain': [1, 2, 3, 4, 5, 6],
                        'force': [3]
                    },
                    {
                        'constraints': [['poly', 'rbf', 'sigmoid']],
                        'name': 'gamma',
                        'domain': [0.03, 0.06, 0.1, 0.13, 0.16, 0.2],
                        'force': [0.1]
                    },
                    {
                        'constraints': [['poly', 'sigmoid']],
                        'name': 'coef0',
                        'domain': np.arange(0.0, 1.0, 0.1),
                        'force': [0.0]
                    }
                ]
            }
        ]
    },
    {
        'name': 'data',
        'domain': ['SamsungPolandMappingSets2016', 'NormalSets2016', 'NormalSets2015', 'Normal2012', 'Normal2015', 'Normal2016', 'CrossValidation2015', 'CrossValidation2016', 'CrossValidation2017'],
        'disabled': False,
#         'force': ['CrossValidation2016', 'Normal2016'],
        'force': ['CrossValidation2017'],
#         'force': ['CrossValidation2016'],
        'subparams':
        [
            {
                'constraints': [['CrossValidation2015', 'CrossValidation2016', 'CrossValidation2017']],
                'name': 'partsCount',
                'domain': [3, 5, 10, 20],
                'force': [10]
            }
        ]
    },
    {
        'name': 'agParser',
        'domain': [True],
        'subparams':
        [
            {
                'name': 'removeStopWords',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'removePunct',
                'domain': [True, False],
                'force': [False]
            },
            {
                'name': 'toLowerCase',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'lemma',
                'domain': [True, False],
                'force': [True]
            }
        ]
    },
    {
        'name': 'LengthFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [True],
        'subparams':
        [
            {
                'name': 'string',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'tokens',
                'domain': [True, False],
                'force': [True]
            }
        ]
    },
    {
        'name': 'SentencePairFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [False],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'sameUpperCaseCount',
                'domain': [True, False],
                'force': [False]
            },
            {
                'constraints': [[True]],
                'name': 'sameLemmaCount',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [[True]],
                'name': 'word',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'stringLength', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'substraction', 'domain': [True, False], 'force': [True] },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'punct',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'stopword',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'smallsw3', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'bigsw1', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'nltksw', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'swTokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'stringLength', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'substraction', 'domain': [True, False], 'force': [True] },
                ]
            },
        ]
    },
    {
        'name': 'SultanAlignerFeature',
        'domain': [True, False],
        'disabled': True,
        'force': [True],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'similarity1',
                'domain': [True, False],
                'force': [True],
            },
            {
                'constraints': [[True]],
                'name': 'similarity2',
                'domain': [True, False],
                'force': [True],
            }
        ]
    },
    {
        'name': 'Word2VecFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [True],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'homeMadeSimilarity',
                'domain': [True, False],
                'force': [False],
            },
            {
                'constraints': [[True]],
                'name': 'w2vNSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0], # best 0.0 pour brown_stsall et 1.0 pour GoogleNews
                        'force': [0.0]
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            },
            { 
                'constraints': [[True]],
                'name': 'data',
                'domain': ['brown_stsall', 'brown', 'stsall', 'BaroniVectors', 'GoogleNews'],
                'force': ['brown_stsall'], # best GoogleNews then brown_stsall
                'subparams':
                [
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'min_count',
                        'sorted': True,
                        'domain': [0, 1, 3, 7, 15, 200],
                        # 'force': [5, 15]
                        'force': [0]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'window',
                        'sorted': True,
                        'domain': [1, 2, 3, 4, 5, 6, 7, 8],
                        'force': [3, 8]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'size',
                        'sorted': True,
                        'domain': [50, 100, 500, 3000],
                        'force': [100, 3000]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'removeStopWords',
                        'domain': [True, False],
                        # 'force': [False]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'removePunct',
                        'domain': [True, False],
                        'force': [False]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'toLowerCase',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'lemma',
                        'domain': [True, False],
                        # 'force': [True]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'dataPart',
                        'sorted': True,
                        'domain': [0.1, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0],
                        'force': [1.0]
                    },
                ]
            }
        ]
    },
    {
        'name': 'RandomFeature',
        'domain': [True, False],
        'disabled': True,
        'force': [False]
    },
    {
        'name': 'MultiDoc2VecFeature',
        'domain': [True, False],
        'force': [True],
        'disabled': True,
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'd2vSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0],
                        # 'force': [0.0, 0.5, 1.0],
                        'force': [0.0],
                        
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            },
            {
                'constraints': [[True]],
                'name': 'fileIdSet',
                'domain':
                [
                    [
                        "_s100_w2_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
                        "_s100_w2_mc0_a0.1_i22_sa0.000101_lemma_nopunct_lowercase_brown_part0.75",
                        "_s100_w3_mc0_a0.08_i22_sa0.00012_lemma_nostopword_nopunct_lowercase_brown_part0.75",
                        "_s100_w1_mc0_a0.06_i22_sa6e-05_lowercase_brown_part0.75",
                        "_s100_w2_mc0_a0.06_i22_sa6e-05_nopunct_lowercase_brown_part0.75",
                        "_s100_w1_mc0_a0.08_i22_sa6e-05_lemma_lowercase_brown_part0.5",
                        "_s100_w1_mc0_a0.08_i22_sa6e-05_lemma_lowercase_stsall",
                        "_s100_w3_mc0_a0.1_i22_lemma_nopunct_lowercase_brown_part0.96",
                        "_s100_w3_mc0_a0.11_i21_lemma_nopunct_lowercase_brown_part0.25",
                        "_s100_w3_mc0_a0.1_i22_n1_lemma_nopunct_lowercase_brown_part0.75",
                        "_s100_w2_mc0_a0.1_i22_n8_lemma_nopunct_lowercase_brown_part0.75",
                        "_s100_w2_mc0_a0.1_i22_n4_lemma_nopunct_lowercase_brown_part0.75",
                        "_s100_w2_mc7_a0.1_i20_lemma_nopunct_lowercase_brown_part0.75",
                        "_s3000_w8_mc200_a0.1_i20_n5_lemma_nopunct_lowercase_brown_part0.75",
                        "_s100_w1_mc0_a0.08_i22_sa6e-05_lemma_lowercase_brown_part0.75",
                        "_s100_w3_mc0_a0.078_i22_sa6e-05_lemma_lowercase_brown_part0.75",
                        "_s120_w2_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s150_w1_mc0_a0.07_i22_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s220_w1_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s150_w2_mc0_a0.07_i22_sa8e-05_lemma_lowercase_brown_part0.75",
#                         "_s500_w1_mc0_a0.066_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s1000_w1_mc0_a0.068_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s3000_w1_mc0_a0.064_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s4400_w1_mc0_a0.07_i15_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s100_w6_mc0_a0.068_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s4000_w10_mc0_a0.1_i10_lemma_nopunct_lowercase_brown_part0.5",
#                         "_s4000_w15_mc0_a0.12_i10_sa1e-05_lemma_nopunct_lowercase_brown_part0.5",
#                         "_s120_w1_mc0_a0.07_i22_sa8e-05_lemma_lowercase_brown_part0.75",
#                         "_s180_w1_mc0_a0.07_i15_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s200_w1_mc0_a0.068_i15_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s350_w1_mc0_a0.068_i15_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s180_w2_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s120_w3_mc0_a0.068_i22_sa8e-05_lemma_lowercase_brown_part0.75",
#                         "_s260_w1_mc0_a0.068_i15_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s280_w1_mc0_a0.07_i15_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s450_w1_mc0_a0.068_i15_sa8e-05_lemma_lowercase_brown_part0.75",
#                         "_s400_w1_mc0_a0.07_i15_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s200_w2_mc0_a0.07_i22_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s6000_w1_mc0_a0.07_i22_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s900_w1_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s260_w2_mc0_a0.068_i22_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s120_w4_mc0_a0.068_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s1500_w1_mc0_a0.068_i15_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s150_w3_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s220_w2_mc0_a0.068_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s600_w1_mc0_a0.068_i15_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s2500_w1_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s550_w1_mc0_a0.068_i15_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s300_w1_mc0_a0.07_i22_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s700_w1_mc0_a0.068_i15_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s400_w2_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s180_w3_mc0_a0.07_i22_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s5000_w1_mc0_a0.07_i15_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s800_w1_mc0_a0.068_i15_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s140_w2_mc0_a0.1_i22_sa6.8e-05_lemma_nopunct_lowercase_brown_part0.75",
#                         "_s280_w2_mc0_a0.068_i15_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s3500_w1_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s1300_w1_mc0_a0.07_i15_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s80_w1_mc0_a0.07_i22_sa8e-05_lemma_lowercase_brown_part0.75",
#                         "_s4000_w1_mc0_a0.068_i22_sa6e-05_lemma_lowercase_brown_part0.75"
                    ]
                ]
            }
        ]
    },
    {
        'name': 'Doc2VecFeature',
        'domain': [True, False],
        'force': [False],
        'disabled': False,
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'data',
                'domain': ['ukwac', 'enwiki', 'ukwac_enwiki', 'halfukwac', 'brown', 'stsall'],
                # 'force': ['brown', 'stsall'],
                # 'force': ['ukwac'],
                'force': ['brown'],
                'subparams':
                [
                    {
                        'name': 'sample',
                        'sorted': True,
                        'default': 0.0,
                        'domain': [0.0, 1e-5],
                        # 'force': np.arange(0.00034, 0.00037, 0.000001)
                        'force': [0.0]
                    },
                    {
                        'name': 'iter',
                        'sorted': True,
                        'default': 5,
                        'domain': range(1, 20, 1),
                        'force': [5]
                    },
                    {
                        'name': 'negative',
                        'sorted': True,
                        'default': 0,
                        'domain': range(5, 20, 1),
                        'force': [0]
                    },
                    {
                        'name': 'alpha',
                        'default': 0.025,
                        'sorted': True,
                        'domain': [0.005, 0.010, 0.015, 0.020, 0.025, 0.030, 0.035, 0.040, 0.045],
                        # 'force': [5, 15]
#                         'force': [0.045, 0.7, 0.8, 0.9, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.2, 0.3, 0.4, 0.5]
#                         'force': [0.045, 0.1, 0.2, 0.3, 0.4, 0.5]
#                         'force': np.arange(0.07, 0.15, 0.01)
                        'force': [0.025]
                    },
                    {
                        'name': 'min_count',
                        'sorted': True,
                        'domain': [0, 1, 3, 7, 15, 200],
                        # 'force': [5, 15]
                        'force': [0]
                    },
                    {
                        'name': 'window',
                        'sorted': True,
                        'domain': [3, 8],
                        # 'force': [1, 2, 3, 8]
                        # 'force': [1, 2, 3, 4, 5, 6, 7, 8]
                    },
                    {
                        'name': 'size',
                        'sorted': True,
                        'domain': [50, 100, 500, 3000],
                        'force': [100, 3000]
                    },
                    {
                        'name': 'removeStopWords',
                        'domain': [True, False],
                        # 'force': [False]
                    },
                    {
                        'name': 'removePunct',
                        'domain': [True, False],
                        'force': [False]
                    },
                    {
                        'name': 'toLowerCase',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'name': 'lemma',
                        'domain': [True, False],
                        # 'force': [True]
                    },
                    {
                        'name': 'dataPart',
                        'sorted': True,
                        'domain': [0.1, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0],
                        # 'force': [0.0, 0.25, 0.5, 0.75, 1.0]
                        # 'force': [0.0, 0.5, 1.0]
                        # 'force': [0.0, 1.0]
                        # 'force': [0.0, 0.5, 1.0]
                        'force': [1.0]
                    },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'd2vSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0],
                        # 'force': [0.0, 0.5, 1.0],
                        'force': [0.0],
                        
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            }
        ]
    }
]

###############################################################################
############################### sets2016CombsDef ##################################
###############################################################################

sets2016CombsDef = \
[
    {
        'name': 'score',
        'domain': ['MeanLeastSquares', 'MeanDifference', 'ScipyPearsonCorrelation', 'NumpyPearsonCorrelation', 'AgirrePearsonCorrelation'],
        'force': ['NumpyPearsonCorrelation']
    },
    {
        'name': 'regressor',
        'domain': ['KernelRidge', 'LinearRegression', 'Ridge', 'RidgeCV', 'Lasso', 'ElasticNet', 'LinearSVR', 'SVR', 'NuSVR'],
        'force': ['Ridge'],
        # 'force': ['LinearSVR', 'SVR', 'NuSVR'],
        'subparams':
        [
            {
                'constraints': [['Ridge', 'RidgeCV', 'Lasso', 'ElasticNet', 'KernelRidge']],
                'name': 'alpha',
                'domain': np.arange(0.1, 3.0, 0.1),
                'force': [2.7]
            },
            {
                'constraints': [['ElasticNet']],
                'name': 'l1_ratio',
                'domain': np.arange(0.0, 1.0, 0.1),
                'force': [0.5]
            },
            {
                'constraints': [['SVR', 'LinearSVR']],
                'name': 'epsilon',
                'domain': [0.03, 0.06, 0.1, 0.13, 0.16, 0.2],
                'force': [0.1]
            },
            {
                'constraints': [['NuSVR']],
                'name': 'nu',
                'domain': np.arange(0.1, 1.0, 0.1),
                'force': [0.5]
            },
            {
                'constraints': [['SVR', 'NuSVR', 'LinearSVR']],
                'name': 'C',
                'domain': [0.1, 0.5, 1.0, 1.5, 2.0],
                'force': [1.0]
            },
            {
                'constraints': [['SVR', 'NuSVR']],
                'name': 'shrinking',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [['LinearSVR']],
                'name': 'dual',
                'domain': [True, False],
                'force': [False]
            },
            {
                'constraints': [['SVR', 'NuSVR', 'KernelRidge']],
                'name': 'kernel',
                'domain': ['linear', 'poly', 'rbf', 'sigmoid', 'precomputed'],
                'force': ['rbf'],
                'subparams':
                [
                    {
                        'constraints': [['poly']],
                        'name': 'degree',
                        'domain': [1, 2, 3, 4, 5, 6],
                        'force': [3]
                    },
                    {
                        'constraints': [['poly', 'rbf', 'sigmoid']],
                        'name': 'gamma',
                        'domain': [0.03, 0.06, 0.1, 0.13, 0.16, 0.2],
                        'force': [0.1]
                    },
                    {
                        'constraints': [['poly', 'sigmoid']],
                        'name': 'coef0',
                        'domain': np.arange(0.0, 1.0, 0.1),
                        'force': [0.0]
                    }
                ]
            }
        ]
    },
    {
        'name': 'data',
        'domain': ['SamsungPolandMappingSets2016', 'NormalSets2016', 'NormalSets2015', 'Normal2012', 'Normal2015', 'Normal2016', 'CrossValidation2015', 'CrossValidation2016', 'CrossValidation2017'],
        'disabled': False,
        'force': ['NormalSets2016'],
        'subparams':
        [
            {
                'constraints': [['CrossValidation2015', 'CrossValidation2016', 'CrossValidation2017']],
                'name': 'partsCount',
                'domain': [3, 5, 10, 20],
                'force': [10]
            }
        ]
    },
    {
        'name': 'agParser',
        'domain': [True],
        'subparams':
        [
            {
                'name': 'removeStopWords',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'removePunct',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'toLowerCase',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'lemma',
                'domain': [True, False],
                'force': [False]
            }
        ]
    },
    {
        'name': 'LengthFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [False],
        'subparams':
        [
            {
                'name': 'string',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'tokens',
                'domain': [True, False],
                'force': [True]
            }
        ]
    },
    {
        'name': 'SentencePairFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [True],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'sameUpperCaseCount',
                'domain': [True, False],
                'force': [False]
            },
            {
                'constraints': [[True]],
                'name': 'sameLemmaCount',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [[True]],
                'name': 'word',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'stringLength', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'substraction', 'domain': [True, False], 'force': [True] },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'punct',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'stopword',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'smallsw3', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'bigsw1', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'nltksw', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'swTokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'stringLength', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'substraction', 'domain': [True, False], 'force': [True] },
                ]
            },
        ]
    },
    {
        'name': 'SultanAlignerFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [True],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'similarity1',
                'domain': [True, False],
                'force': [True],
            },
            {
                'constraints': [[True]],
                'name': 'similarity2',
                'domain': [True, False],
                'force': [True],
            }
        ]
    },
    {
        'name': 'Word2VecFeature',
        'domain': [True, False],
        'disabled': True,
        'force': [True],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'homeMadeSimilarity',
                'domain': [True, False],
                'force': [False],
            },
            {
                'constraints': [[True]],
                'name': 'w2vNSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0], # best 0.0 pour brown_stsall et 1.0 pour GoogleNews
                        'force': [0.0]
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            },
            { 
                'constraints': [[True]],
                'name': 'data',
                'domain': ['brown_stsall', 'brown', 'stsall', 'BaroniVectors', 'GoogleNews'],
                'force': ['brown_stsall'], # best GoogleNews then brown_stsall
                'subparams':
                [
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'min_count',
                        'sorted': True,
                        'domain': [0, 1, 3, 7, 15, 200],
                        # 'force': [5, 15]
                        'force': [0]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'window',
                        'sorted': True,
                        'domain': [1, 2, 3, 4, 5, 6, 7, 8],
                        'force': [3, 8]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'size',
                        'sorted': True,
                        'domain': [50, 100, 500, 3000],
                        'force': [100, 3000]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'removeStopWords',
                        'domain': [True, False],
                        # 'force': [False]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'removePunct',
                        'domain': [True, False],
                        'force': [False]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'toLowerCase',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'lemma',
                        'domain': [True, False],
                        # 'force': [True]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'dataPart',
                        'sorted': True,
                        'domain': [0.1, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0],
                        'force': [1.0]
                    },
                ]
            }
        ]
    },
    {
        'name': 'RandomFeature',
        'domain': [True, False],
        'disabled': True,
        'force': [False]
    },
    {
        'name': 'MultiDoc2VecFeature',
        'domain': [True, False],
        'force': [True],
        'disabled': False,
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'd2vSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0],
                        # 'force': [0.0, 0.5, 1.0],
                        'force': [0.0],
                        
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            },
            {
                'constraints': [[True]],
                'name': 'fileIdSet',
                'domain':
                [
                    [
                        "_s100_w2_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
                        "_s100_w2_mc0_a0.1_i22_sa0.000101_lemma_nopunct_lowercase_brown_part0.75",
                        "_s100_w3_mc0_a0.08_i22_sa0.00012_lemma_nostopword_nopunct_lowercase_brown_part0.75",
                        "_s100_w1_mc0_a0.06_i22_sa6e-05_lowercase_brown_part0.75",
                        "_s100_w2_mc0_a0.06_i22_sa6e-05_nopunct_lowercase_brown_part0.75",
                        "_s100_w1_mc0_a0.08_i22_sa6e-05_lemma_lowercase_brown_part0.5",
                        "_s100_w1_mc0_a0.08_i22_sa6e-05_lemma_lowercase_stsall",
                        "_s100_w3_mc0_a0.1_i22_lemma_nopunct_lowercase_brown_part0.96",
                        "_s100_w3_mc0_a0.11_i21_lemma_nopunct_lowercase_brown_part0.25",
                        "_s100_w3_mc0_a0.1_i22_n1_lemma_nopunct_lowercase_brown_part0.75",
                        "_s100_w2_mc0_a0.1_i22_n8_lemma_nopunct_lowercase_brown_part0.75",
                        "_s100_w2_mc0_a0.1_i22_n4_lemma_nopunct_lowercase_brown_part0.75",
                        "_s100_w2_mc7_a0.1_i20_lemma_nopunct_lowercase_brown_part0.75",
                        "_s3000_w8_mc200_a0.1_i20_n5_lemma_nopunct_lowercase_brown_part0.75",
                        "_s100_w1_mc0_a0.08_i22_sa6e-05_lemma_lowercase_brown_part0.75",
                        "_s100_w3_mc0_a0.078_i22_sa6e-05_lemma_lowercase_brown_part0.75",
                        "_s120_w2_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s150_w1_mc0_a0.07_i22_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s220_w1_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s150_w2_mc0_a0.07_i22_sa8e-05_lemma_lowercase_brown_part0.75",
#                         "_s500_w1_mc0_a0.066_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s1000_w1_mc0_a0.068_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s3000_w1_mc0_a0.064_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s4400_w1_mc0_a0.07_i15_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s100_w6_mc0_a0.068_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s4000_w10_mc0_a0.1_i10_lemma_nopunct_lowercase_brown_part0.5",
#                         "_s4000_w15_mc0_a0.12_i10_sa1e-05_lemma_nopunct_lowercase_brown_part0.5",
#                         "_s120_w1_mc0_a0.07_i22_sa8e-05_lemma_lowercase_brown_part0.75",
#                         "_s180_w1_mc0_a0.07_i15_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s200_w1_mc0_a0.068_i15_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s350_w1_mc0_a0.068_i15_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s180_w2_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s120_w3_mc0_a0.068_i22_sa8e-05_lemma_lowercase_brown_part0.75",
#                         "_s260_w1_mc0_a0.068_i15_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s280_w1_mc0_a0.07_i15_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s450_w1_mc0_a0.068_i15_sa8e-05_lemma_lowercase_brown_part0.75",
#                         "_s400_w1_mc0_a0.07_i15_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s200_w2_mc0_a0.07_i22_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s6000_w1_mc0_a0.07_i22_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s900_w1_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s260_w2_mc0_a0.068_i22_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s120_w4_mc0_a0.068_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s1500_w1_mc0_a0.068_i15_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s150_w3_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s220_w2_mc0_a0.068_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s600_w1_mc0_a0.068_i15_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s2500_w1_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s550_w1_mc0_a0.068_i15_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s300_w1_mc0_a0.07_i22_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s700_w1_mc0_a0.068_i15_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s400_w2_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s180_w3_mc0_a0.07_i22_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s5000_w1_mc0_a0.07_i15_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s800_w1_mc0_a0.068_i15_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s140_w2_mc0_a0.1_i22_sa6.8e-05_lemma_nopunct_lowercase_brown_part0.75",
#                         "_s280_w2_mc0_a0.068_i15_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s3500_w1_mc0_a0.07_i22_sa6e-05_lemma_lowercase_brown_part0.75",
#                         "_s1300_w1_mc0_a0.07_i15_sa6.2e-05_lemma_lowercase_brown_part0.75",
#                         "_s80_w1_mc0_a0.07_i22_sa8e-05_lemma_lowercase_brown_part0.75",
#                         "_s4000_w1_mc0_a0.068_i22_sa6e-05_lemma_lowercase_brown_part0.75"
                    ]
                ]
            }
        ]
    },
    {
        'name': 'Doc2VecFeature',
        'domain': [True, False],
        'force': [True],
        'disabled': True,
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'data',
                'domain': ['ukwac', 'enwiki', 'ukwac_enwiki', 'halfukwac', 'brown', 'stsall'],
                # 'force': ['brown', 'stsall'],
                # 'force': ['ukwac'],
                'force': ['brown'],
                'subparams':
                [
                    {
                        'name': 'sample',
                        'sorted': True,
                        'default': 0.0,
                        'domain': [0.0, 1e-5],
                        # 'force': np.arange(0.00034, 0.00037, 0.000001)
                        'force': [0.0]
                    },
                    {
                        'name': 'iter',
                        'sorted': True,
                        'default': 5,
                        'domain': range(1, 20, 1),
                        'force': [22]
                    },
                    {
                        'name': 'negative',
                        'sorted': True,
                        'default': 0,
                        'domain': range(5, 20, 1),
                        'force': [0]
                    },
                    {
                        'name': 'alpha',
                        'default': 0.025,
                        'sorted': True,
                        'domain': [0.005, 0.010, 0.015, 0.020, 0.025, 0.030, 0.035, 0.040, 0.045],
                        # 'force': [5, 15]
#                         'force': [0.045, 0.7, 0.8, 0.9, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.2, 0.3, 0.4, 0.5]
#                         'force': [0.045, 0.1, 0.2, 0.3, 0.4, 0.5]
#                         'force': np.arange(0.07, 0.15, 0.01)
                        'force': [0.1]
                    },
                    {
                        'name': 'min_count',
                        'sorted': True,
                        'domain': [0, 1, 3, 7, 15, 200],
                        # 'force': [5, 15]
                        'force': [0]
                    },
                    {
                        'name': 'window',
                        'sorted': True,
                        'domain': [2, 3, 8],
                        # 'force': [1, 2, 3, 8]
                        # 'force': [1, 2, 3, 4, 5, 6, 7, 8]
                    },
                    {
                        'name': 'size',
                        'sorted': True,
                        'domain': [50, 100, 500, 3000],
                        'force': [10, 50, 100, 120, 140, 160, 180, 200, 250, 300, 400, 500, 600, 800, 1000, 1200, 1500, 2000, 2500, 3000, 4000, 4400, 5000, 6000, 7000]
                    },
                    {
                        'name': 'removeStopWords',
                        'domain': [True, False],
                        'force': [False]
                    },
                    {
                        'name': 'removePunct',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'name': 'toLowerCase',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'name': 'lemma',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'name': 'dataPart',
                        'sorted': True,
                        'domain': [0.1, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0],
                        # 'force': [0.0, 0.25, 0.5, 0.75, 1.0]
                        # 'force': [0.0, 0.5, 1.0]
                        # 'force': [0.0, 1.0]
                        # 'force': [0.0, 0.5, 1.0]
                        'force': [0.75]
                    },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'd2vSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0],
                        # 'force': [0.0, 0.5, 1.0],
                        'force': [0.0],
                        
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            }
        ]
    }
]

###############################################################################
############################### alignementCombsDef ##################################
###############################################################################

alignementCombsDef = \
[
    {
        'name': 'score',
        'domain': ['MeanLeastSquares', 'MeanDifference', 'ScipyPearsonCorrelation', 'NumpyPearsonCorrelation', 'AgirrePearsonCorrelation'],
        'force': ['NumpyPearsonCorrelation']
    },
    {
        'name': 'regressor',
        'domain': ['KernelRidge', 'LinearRegression', 'Ridge', 'RidgeCV', 'Lasso', 'ElasticNet', 'LinearSVR', 'SVR', 'NuSVR'],
        'force': ['Ridge'],
        # 'force': ['LinearSVR', 'SVR', 'NuSVR'],
        'subparams':
        [
            {
                'constraints': [['Ridge', 'RidgeCV', 'Lasso', 'ElasticNet', 'KernelRidge']],
                'name': 'alpha',
                'domain': np.arange(0.1, 3.0, 0.1),
                'force': [2.7]
            },
            {
                'constraints': [['ElasticNet']],
                'name': 'l1_ratio',
                'domain': np.arange(0.0, 1.0, 0.1),
                'force': [0.5]
            },
            {
                'constraints': [['SVR', 'LinearSVR']],
                'name': 'epsilon',
                'domain': [0.03, 0.06, 0.1, 0.13, 0.16, 0.2],
                'force': [0.1]
            },
            {
                'constraints': [['NuSVR']],
                'name': 'nu',
                'domain': np.arange(0.1, 1.0, 0.1),
                'force': [0.5]
            },
            {
                'constraints': [['SVR', 'NuSVR', 'LinearSVR']],
                'name': 'C',
                'domain': [0.1, 0.5, 1.0, 1.5, 2.0],
                'force': [1.0]
            },
            {
                'constraints': [['SVR', 'NuSVR']],
                'name': 'shrinking',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [['LinearSVR']],
                'name': 'dual',
                'domain': [True, False],
                'force': [False]
            },
            {
                'constraints': [['SVR', 'NuSVR', 'KernelRidge']],
                'name': 'kernel',
                'domain': ['linear', 'poly', 'rbf', 'sigmoid', 'precomputed'],
                'force': ['rbf'],
                'subparams':
                [
                    {
                        'constraints': [['poly']],
                        'name': 'degree',
                        'domain': [1, 2, 3, 4, 5, 6],
                        'force': [3]
                    },
                    {
                        'constraints': [['poly', 'rbf', 'sigmoid']],
                        'name': 'gamma',
                        'domain': [0.03, 0.06, 0.1, 0.13, 0.16, 0.2],
                        'force': [0.1]
                    },
                    {
                        'constraints': [['poly', 'sigmoid']],
                        'name': 'coef0',
                        'domain': np.arange(0.0, 1.0, 0.1),
                        'force': [0.0]
                    }
                ]
            }
        ]
    },
    {
        'name': 'data',
        'domain': ['SamsungPolandMappingSets2016', 'NormalSets2016', 'NormalSets2015', 'Normal2012', 'Normal2015', 'Normal2016', 'CrossValidation2015', 'CrossValidation2016', 'CrossValidation2017'],
        'disabled': False,
        'force': ['Normal2016'],
        'subparams':
        [
            {
                'constraints': [['CrossValidation2015', 'CrossValidation2016', 'CrossValidation2017']],
                'name': 'partsCount',
                'domain': [3, 5, 10, 20],
                'force': [10]
            }
        ]
    },
    {
        'name': 'agParser',
        'domain': [True],
        'subparams':
        [
            {
                'name': 'removeStopWords',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'removePunct',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'toLowerCase',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'lemma',
                'domain': [True, False],
                'force': [False]
            }
        ]
    },
    {
        'name': 'LengthFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [True],
        'subparams':
        [
            {
                'name': 'string',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'tokens',
                'domain': [True, False],
                'force': [True]
            }
        ]
    },
    {
        'name': 'SentencePairFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [False],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'sameUpperCaseCount',
                'domain': [True, False],
                'force': [False]
            },
            {
                'constraints': [[True]],
                'name': 'sameLemmaCount',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [[True]],
                'name': 'word',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'stringLength', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'substraction', 'domain': [True, False], 'force': [True] },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'punct',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'stopword',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'smallsw3', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'bigsw1', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'nltksw', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'swTokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'stringLength', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'substraction', 'domain': [True, False], 'force': [True] },
                ]
            },
        ]
    },
    {
        'name': 'SultanAlignerFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [True],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'similarity1',
                'domain': [True, False],
                'force': [True],
            },
            {
                'constraints': [[True]],
                'name': 'similarity2',
                'domain': [True, False],
                'force': [True],
            }
        ]
    },
    {
        'name': 'Word2VecFeature',
        'domain': [True, False],
        'disabled': True,
        'force': [False],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'homeMadeSimilarity',
                'domain': [True, False],
                'force': [False],
            },
            {
                'constraints': [[True]],
                'name': 'w2vNSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0], # best 0.0 pour brown_stsall et 1.0 pour GoogleNews
                        'force': [0.0]
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            },
            { 
                'constraints': [[True]],
                'name': 'data',
                'domain': ['brown_stsall', 'brown', 'stsall', 'BaroniVectors', 'GoogleNews'],
                'force': ['brown_stsall'], # best GoogleNews then brown_stsall
                'subparams':
                [
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'min_count',
                        'sorted': True,
                        'domain': [0, 1, 3, 7, 15, 200],
                        # 'force': [5, 15]
                        'force': [0]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'window',
                        'sorted': True,
                        'domain': [1, 2, 3, 4, 5, 6, 7, 8],
                        'force': [3, 8]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'size',
                        'sorted': True,
                        'domain': [50, 100, 500, 3000],
                        'force': [100, 3000]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'removeStopWords',
                        'domain': [True, False],
                        # 'force': [False]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'removePunct',
                        'domain': [True, False],
                        'force': [False]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'toLowerCase',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'lemma',
                        'domain': [True, False],
                        # 'force': [True]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'dataPart',
                        'sorted': True,
                        'domain': [0.1, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0],
                        'force': [1.0]
                    },
                ]
            }
        ]
    },
    {
        'name': 'RandomFeature',
        'domain': [True, False],
        'disabled': True,
        'force': [False]
    },
    {
        'name': 'MultiDoc2VecFeature',
        'domain': [True, False],
        'force': [True],
        'disabled': False,
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'd2vSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0],
                        # 'force': [0.0, 0.5, 1.0],
                        'force': [0.0],
                        
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            },
            {
                'constraints': [[True]],
                'name': 'fileIdSet',
                'domain':
                [
                        [
                            "_s100_w2_mc0_a0.1_i22_sa0.000101_lemma_nopunct_lowercase_brown_part0.75",
                        ]
                ]
            }
        ]
    },
    {
        'name': 'Doc2VecFeature',
        'domain': [True, False],
        'force': [True],
        'disabled': True,
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'data',
                'domain': ['ukwac', 'enwiki', 'ukwac_enwiki', 'halfukwac', 'brown', 'stsall'],
                # 'force': ['brown', 'stsall'],
                # 'force': ['ukwac'],
                'force': ['brown'],
                'subparams':
                [
                    {
                        'name': 'sample',
                        'sorted': True,
                        'default': 0.0,
                        'domain': [0.0, 1e-5],
                        # 'force': np.arange(0.00034, 0.00037, 0.000001)
                        'force': [0.0]
                    },
                    {
                        'name': 'iter',
                        'sorted': True,
                        'default': 5,
                        'domain': range(1, 20, 1),
                        'force': [22]
                    },
                    {
                        'name': 'negative',
                        'sorted': True,
                        'default': 0,
                        'domain': range(5, 20, 1),
                        'force': [0]
                    },
                    {
                        'name': 'alpha',
                        'default': 0.025,
                        'sorted': True,
                        'domain': [0.005, 0.010, 0.015, 0.020, 0.025, 0.030, 0.035, 0.040, 0.045],
                        # 'force': [5, 15]
#                         'force': [0.045, 0.7, 0.8, 0.9, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.2, 0.3, 0.4, 0.5]
#                         'force': [0.045, 0.1, 0.2, 0.3, 0.4, 0.5]
#                         'force': np.arange(0.07, 0.15, 0.01)
                        'force': [0.1]
                    },
                    {
                        'name': 'min_count',
                        'sorted': True,
                        'domain': [0, 1, 3, 7, 15, 200],
                        # 'force': [5, 15]
                        'force': [0]
                    },
                    {
                        'name': 'window',
                        'sorted': True,
                        'domain': [2, 3, 8],
                        # 'force': [1, 2, 3, 8]
                        # 'force': [1, 2, 3, 4, 5, 6, 7, 8]
                    },
                    {
                        'name': 'size',
                        'sorted': True,
                        'domain': [50, 100, 500, 3000],
                        'force': [10, 50, 100, 120, 140, 160, 180, 200, 250, 300, 400, 500, 600, 800, 1000, 1200, 1500, 2000, 2500, 3000, 4000, 4400, 5000, 6000, 7000]
                    },
                    {
                        'name': 'removeStopWords',
                        'domain': [True, False],
                        'force': [False]
                    },
                    {
                        'name': 'removePunct',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'name': 'toLowerCase',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'name': 'lemma',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'name': 'dataPart',
                        'sorted': True,
                        'domain': [0.1, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0],
                        # 'force': [0.0, 0.25, 0.5, 0.75, 1.0]
                        # 'force': [0.0, 0.5, 1.0]
                        # 'force': [0.0, 1.0]
                        # 'force': [0.0, 0.5, 1.0]
                        'force': [0.75]
                    },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'd2vSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0],
                        # 'force': [0.0, 0.5, 1.0],
                        'force': [0.0],
                        
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            }
        ]
    }
]


###############################################################################
############################### multiDoc2VecCombsDef ##################################
###############################################################################

multiDoc2VecCombsDef = \
[
    {
        'name': 'score',
        'domain': ['MeanLeastSquares', 'MeanDifference', 'ScipyPearsonCorrelation', 'NumpyPearsonCorrelation', 'AgirrePearsonCorrelation'],
        'force': ['NumpyPearsonCorrelation']
    },
    {
        'name': 'regressor',
        'domain': ['KernelRidge', 'LinearRegression', 'Ridge', 'RidgeCV', 'Lasso', 'ElasticNet', 'LinearSVR', 'SVR', 'NuSVR'],
        'force': ['Ridge'],
        # 'force': ['LinearSVR', 'SVR', 'NuSVR'],
        'subparams':
        [
            {
                'constraints': [['Ridge', 'RidgeCV', 'Lasso', 'ElasticNet', 'KernelRidge']],
                'name': 'alpha',
                'domain': np.arange(0.1, 3.0, 0.1),
                'force': [2.7]
            },
            {
                'constraints': [['ElasticNet']],
                'name': 'l1_ratio',
                'domain': np.arange(0.0, 1.0, 0.1),
                'force': [0.5]
            },
            {
                'constraints': [['SVR', 'LinearSVR']],
                'name': 'epsilon',
                'domain': [0.03, 0.06, 0.1, 0.13, 0.16, 0.2],
                'force': [0.1]
            },
            {
                'constraints': [['NuSVR']],
                'name': 'nu',
                'domain': np.arange(0.1, 1.0, 0.1),
                'force': [0.5]
            },
            {
                'constraints': [['SVR', 'NuSVR', 'LinearSVR']],
                'name': 'C',
                'domain': [0.1, 0.5, 1.0, 1.5, 2.0],
                'force': [1.0]
            },
            {
                'constraints': [['SVR', 'NuSVR']],
                'name': 'shrinking',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [['LinearSVR']],
                'name': 'dual',
                'domain': [True, False],
                'force': [False]
            },
            {
                'constraints': [['SVR', 'NuSVR', 'KernelRidge']],
                'name': 'kernel',
                'domain': ['linear', 'poly', 'rbf', 'sigmoid', 'precomputed'],
                'force': ['rbf'],
                'subparams':
                [
                    {
                        'constraints': [['poly']],
                        'name': 'degree',
                        'domain': [1, 2, 3, 4, 5, 6],
                        'force': [3]
                    },
                    {
                        'constraints': [['poly', 'rbf', 'sigmoid']],
                        'name': 'gamma',
                        'domain': [0.03, 0.06, 0.1, 0.13, 0.16, 0.2],
                        'force': [0.1]
                    },
                    {
                        'constraints': [['poly', 'sigmoid']],
                        'name': 'coef0',
                        'domain': np.arange(0.0, 1.0, 0.1),
                        'force': [0.0]
                    }
                ]
            }
        ]
    },
    {
        'name': 'data',
        'domain': ['SamsungPolandMappingSets2016', 'NormalSets2016', 'NormalSets2015', 'Normal2012', 'Normal2015', 'Normal2016', 'CrossValidation2015', 'CrossValidation2016', 'CrossValidation2017'],
        'disabled': False,
        'force': ['Normal2015'],
        'subparams':
        [
            {
                'constraints': [['CrossValidation2015', 'CrossValidation2016', 'CrossValidation2017']],
                'name': 'partsCount',
                'domain': [3, 5, 10, 20],
                'force': [10]
            },
            {
                'constraints': [['NormalSets2016', 'NormalSets2015', 'SamsungPolandMappingSets2016']],
                'name': 'paperPairsCount',
                'domain': [True, False],
                'force': [False]
            }
        ]
    },
    {
        'name': 'agParser',
        'domain': [True],
        'subparams':
        [
            {
                'name': 'removeStopWords',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'removePunct',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'toLowerCase',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'lemma',
                'domain': [True, False],
                'force': [False]
            }
        ]
    },
    {
        'name': 'LengthFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [True],
        'subparams':
        [
            {
                'name': 'string',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'tokens',
                'domain': [True, False],
                'force': [True]
            }
        ]
    },
    {
        'name': 'SentencePairFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [False],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'sameUpperCaseCount',
                'domain': [True, False],
                'force': [False]
            },
            {
                'constraints': [[True]],
                'name': 'sameLemmaCount',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [[True]],
                'name': 'word',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'stringLength', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'substraction', 'domain': [True, False], 'force': [True] },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'punct',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'stopword',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'smallsw3', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'bigsw1', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'nltksw', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'swTokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'stringLength', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'substraction', 'domain': [True, False], 'force': [True] },
                ]
            },
        ]
    },
    {
        'name': 'SultanAlignerFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [True],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'similarity1',
                'domain': [True, False],
                'force': [True],
            },
            {
                'constraints': [[True]],
                'name': 'similarity2',
                'domain': [True, False],
                'force': [False], # To add for 2016
            },
            {
                'constraints': [[True]],
                'name': 'similarity3', # BEST
                'domain': [True, False],
                'force': [False],
            },
            {
                'constraints': [[True]],
                'name': 'parsingConfigs',
                'domain': [[None]],
                'force':
                [
                    [ # BEST for 2015
                        "isDLS2015SwOrPunct1"
                    ],

#                     [ # BEST for 2016
#                         "_smallsw1",
#                         "_bigsw1",
#                         "isDLS2015SwOrPunct1"
#                     ],
# 
# 
#                     [
#                         "_smallsw3",
#                         "_bigsw1",
#                         "isDLS2015SwOrPunct1"
#                     ],
#                     [
#                         "_bigsw1",
#                         "isDLS2015SwOrPunct1"
#                     ],
#                     [
#                         "_smallsw3"
#                     ],
#                     [
#                         "_smallsw1"
#                     ],
#                     [
#                         "_smallsw1",
#                         "isDLS2015SwOrPunct1"
#                     ],
#                     [
#                         "isDLS2015SwOrPunct1"
#                         "sentsw"
#                     ],
#                     [
#                         "isDLS2015SwOrPunct2"
#                     ],
                ],
            },
        ]
    },
    {
        'name': 'Word2VecFeature',
        'domain': [True, False],
        'disabled': True,
        'force': [False],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'homeMadeSimilarity',
                'domain': [True, False],
                'force': [False],
            },
            {
                'constraints': [[True]],
                'name': 'w2vNSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0], # best 0.0 pour brown_stsall et 1.0 pour GoogleNews
                        'force': [0.0]
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            },
            { 
                'constraints': [[True]],
                'name': 'data',
                'domain': ['brown_stsall', 'brown', 'stsall', 'BaroniVectors', 'GoogleNews'],
                'force': ['brown_stsall'], # best GoogleNews then brown_stsall
                'subparams':
                [
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'min_count',
                        'sorted': True,
                        'domain': [0, 1, 3, 7, 15, 200],
                        # 'force': [5, 15]
                        'force': [0]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'window',
                        'sorted': True,
                        'domain': [1, 2, 3, 4, 5, 6, 7, 8],
                        'force': [3, 8]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'size',
                        'sorted': True,
                        'domain': [50, 100, 500, 3000],
                        'force': [100, 3000]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'removeStopWords',
                        'domain': [True, False],
                        # 'force': [False]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'removePunct',
                        'domain': [True, False],
                        'force': [False]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'toLowerCase',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'lemma',
                        'domain': [True, False],
                        # 'force': [True]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'dataPart',
                        'sorted': True,
                        'domain': [0.1, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0],
                        'force': [1.0]
                    },
                ]
            }
        ]
    },
    {
        'name': 'RandomFeature',
        'domain': [True, False],
        'disabled': True,
        'force': [False]
    },
    {
        'name': 'MultiDoc2VecFeature',
        'domain': [True, False],
        'force': [True],
        'disabled': False,
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'd2vSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0],
                        # 'force': [0.0, 0.5, 1.0],
                        'force': [0.0],
                        
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            },
            {
                'constraints': [[True]],
                'name': 'fileIdSet',
                'domain': [[]],
                'force': [[]],
            },
            {
                'constraints': [[True]],
                'name': 'topdelta',
                'domain': [True, False],
                'force': [False],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'alpha',
                        'domain': [0.2, 0.9],
                        'force': [0.9],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'beta',
                        'domain': [0.2, 1.0],
                        'force': [1.0],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'sigma',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0],
                        'force': [0.5],
#                         'force': [0.8],
#                         'force': [0.5],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'omegas',
                        'domain': [[1.0], [0.7, 0.25, 0.05], [0.5, 0.4, 0.3, 0.1]],
                        #'force': [[0.7, 0.25, 0.05]],
                        'force': [[1.0]],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'beginTopCount',
                        'domain': [0, 1, 2, 3, 4, 5],
                        'force': [1],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'beginByTopdef',
                        'domain': [False],
                        'force': [True],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'fusionSchedule',
                        'domain': [[1, 1], [3, 1], [1, 3], [1, 1, 2, 1], [1, 2], [2, 1], [1, 2, 1, 1]],
#                         'force': [[1, 1, 2, 1], [1, 1], [1, 2, 1, 1]],
#                         'force': [[1, 1, 2, 1]],
#                         'force': [[1, 1]],
                        'force': [[1, 2, 1, 1]],
#                         'force': [[3, 1]],
#                         'force': [[2, 1, 1, 1]],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'infBoundScore',
                        'domain': [0.0, 0.4, 0.7],
                        'force': [0.0],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'maxCount',
                        'domain': [104],
                    },
                    {
                        'constraints': [[True]],
                        'name': 'maxTopDelta',
#                         'domain': range(1, 154, 4),
                        'domain': range(1, 150, 4),
                    },
                ]
            }
        ]
    },
    {
        'name': 'Doc2VecFeature',
        'domain': [True, False],
        'force': [True],
        'disabled': True,
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'data',
                'domain': ['ukwac', 'enwiki', 'ukwac_enwiki', 'halfukwac', 'brown', 'stsall'],
                # 'force': ['brown', 'stsall'],
                # 'force': ['ukwac'],
                'force': ['brown'],
                'subparams':
                [
                    {
                        'name': 'sample',
                        'sorted': True,
                        'default': 0.0,
                        'domain': [0.0, 1e-5],
                        # 'force': np.arange(0.00034, 0.00037, 0.000001)
                        'force': [0.0]
                    },
                    {
                        'name': 'iter',
                        'sorted': True,
                        'default': 5,
                        'domain': range(1, 20, 1),
                        'force': [22]
                    },
                    {
                        'name': 'negative',
                        'sorted': True,
                        'default': 0,
                        'domain': range(5, 20, 1),
                        'force': [0]
                    },
                    {
                        'name': 'alpha',
                        'default': 0.025,
                        'sorted': True,
                        'domain': [0.005, 0.010, 0.015, 0.020, 0.025, 0.030, 0.035, 0.040, 0.045],
                        # 'force': [5, 15]
#                         'force': [0.045, 0.7, 0.8, 0.9, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.2, 0.3, 0.4, 0.5]
#                         'force': [0.045, 0.1, 0.2, 0.3, 0.4, 0.5]
#                         'force': np.arange(0.07, 0.15, 0.01)
                        'force': [0.1]
                    },
                    {
                        'name': 'min_count',
                        'sorted': True,
                        'domain': [0, 1, 3, 7, 15, 200],
                        # 'force': [5, 15]
                        'force': [0]
                    },
                    {
                        'name': 'window',
                        'sorted': True,
                        'domain': [2, 3, 8],
                        # 'force': [1, 2, 3, 8]
                        # 'force': [1, 2, 3, 4, 5, 6, 7, 8]
                    },
                    {
                        'name': 'size',
                        'sorted': True,
                        'domain': [50, 100, 500, 3000],
                        'force': [10, 50, 100, 120, 140, 160, 180, 200, 250, 300, 400, 500, 600, 800, 1000, 1200, 1500, 2000, 2500, 3000, 4000, 4400, 5000, 6000, 7000]
                    },
                    {
                        'name': 'removeStopWords',
                        'domain': [True, False],
                        'force': [False]
                    },
                    {
                        'name': 'removePunct',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'name': 'toLowerCase',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'name': 'lemma',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'name': 'dataPart',
                        'sorted': True,
                        'domain': [0.1, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0],
                        # 'force': [0.0, 0.25, 0.5, 0.75, 1.0]
                        # 'force': [0.0, 0.5, 1.0]
                        # 'force': [0.0, 1.0]
                        # 'force': [0.0, 0.5, 1.0]
                        'force': [0.75]
                    },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'd2vSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0],
                        # 'force': [0.0, 0.5, 1.0],
                        'force': [0.0],
                        
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            }
        ]
    }
]

###############################################################################
############################# d2vBrownCombsDef ################################
###############################################################################

d2vBrownCombsDef = \
[
    {
        'name': 'score',
        'domain': ['MeanLeastSquares', 'MeanDifference', 'ScipyPearsonCorrelation', 'NumpyPearsonCorrelation', 'AgirrePearsonCorrelation'],
        'force': ['NumpyPearsonCorrelation']
    },
    {
        'name': 'regressor',
        'domain': ['KernelRidge', 'LinearRegression', 'Ridge', 'RidgeCV', 'Lasso', 'ElasticNet', 'LinearSVR', 'SVR', 'NuSVR'],
        'force': ['Ridge'],
        # 'force': ['LinearSVR', 'SVR', 'NuSVR'],
        'subparams':
        [
            {
                'constraints': [['Ridge', 'RidgeCV', 'Lasso', 'ElasticNet', 'KernelRidge']],
                'name': 'alpha',
                'domain': list(np.arange(0.1, 3.0, 0.1)),
                'force': [2.7]
            },
            {
                'constraints': [['ElasticNet']],
                'name': 'l1_ratio',
                'domain': list(np.arange(0.0, 1.0, 0.1)),
                'force': [0.5]
            },
            {
                'constraints': [['SVR', 'LinearSVR']],
                'name': 'epsilon',
                'domain': [0.03, 0.06, 0.1, 0.13, 0.16, 0.2],
                'force': [0.1]
            },
            {
                'constraints': [['NuSVR']],
                'name': 'nu',
                'domain': list(np.arange(0.1, 1.0, 0.1)),
                'force': [0.5]
            },
            {
                'constraints': [['SVR', 'NuSVR', 'LinearSVR']],
                'name': 'C',
                'domain': [0.1, 0.5, 1.0, 1.5, 2.0],
                'force': [1.0]
            },
            {
                'constraints': [['SVR', 'NuSVR']],
                'name': 'shrinking',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [['LinearSVR']],
                'name': 'dual',
                'domain': [True, False],
                'force': [False]
            },
            {
                'constraints': [['SVR', 'NuSVR', 'KernelRidge']],
                'name': 'kernel',
                'domain': ['linear', 'poly', 'rbf', 'sigmoid', 'precomputed'],
                'force': ['rbf'],
                'subparams':
                [
                    {
                        'constraints': [['poly']],
                        'name': 'degree',
                        'domain': [1, 2, 3, 4, 5, 6],
                        'force': [3]
                    },
                    {
                        'constraints': [['poly', 'rbf', 'sigmoid']],
                        'name': 'gamma',
                        'domain': [0.03, 0.06, 0.1, 0.13, 0.16, 0.2],
                        'force': [0.1]
                    },
                    {
                        'constraints': [['poly', 'sigmoid']],
                        'name': 'coef0',
                        'domain': list(np.arange(0.0, 1.0, 0.1)),
                        'force': [0.0]
                    }
                ]
            }
        ]
    },
    {
        'name': 'data',
        'domain': ['SamsungPolandMappingSets2016', 'NormalSets2016', 'NormalSets2015', 'Normal2012', 'Normal2015', 'Normal2016', 'CrossValidation2015', 'CrossValidation2016', 'CrossValidation2017'],
        'disabled': False,
        'force': ['CrossValidation2016'],
        'subparams':
        [
            {
                'constraints': [['CrossValidation2015', 'CrossValidation2016', 'CrossValidation2017']],
                'name': 'partsCount',
                'domain': [3, 5, 10, 20],
                'force': [10]
            }
        ]
    },
    {
        'name': 'agParser',
        'domain': [True],
        'subparams':
        [
            {
                'name': 'removeStopWords',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'removePunct',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'toLowerCase',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'lemma',
                'domain': [True, False],
                'force': [False]
            }
        ]
    },
    {
        'name': 'LengthFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [True],
        'subparams':
        [
            {
                'name': 'string',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'tokens',
                'domain': [True, False],
                'force': [True]
            }
        ]
    },
    {
        'name': 'SentencePairFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [False],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'sameUpperCaseCount',
                'domain': [True, False],
                'force': [False]
            },
            {
                'constraints': [[True]],
                'name': 'sameLemmaCount',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [[True]],
                'name': 'word',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'stringLength', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'substraction', 'domain': [True, False], 'force': [True] },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'punct',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'stopword',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'smallsw3', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'bigsw1', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'nltksw', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'swTokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'stringLength', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'substraction', 'domain': [True, False], 'force': [True] },
                ]
            },
        ]
    },
    {
        'name': 'SultanAlignerFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [False],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'similarity1',
                'domain': [True, False],
                'force': [True],
            },
            {
                'constraints': [[True]],
                'name': 'similarity2',
                'domain': [True, False],
                'force': [True],
            }
        ]
    },
    {
        'name': 'Word2VecFeature',
        'domain': [True, False],
        'disabled': True,
        'force': [True],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'homeMadeSimilarity',
                'domain': [True, False],
                'force': [False],
            },
            {
                'constraints': [[True]],
                'name': 'w2vNSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0], # best 0.0 pour brown_stsall et 1.0 pour GoogleNews
                        'force': [0.0]
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            },
            { 
                'constraints': [[True]],
                'name': 'data',
                'domain': ['brown_stsall', 'brown', 'stsall', 'BaroniVectors', 'GoogleNews'],
                'force': ['brown_stsall'], # best GoogleNews then brown_stsall
                'subparams':
                [
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'min_count',
                        'sorted': True,
                        'domain': [0, 1, 3, 7, 15, 200],
                        # 'force': [5, 15]
                        'force': [0]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'window',
                        'sorted': True,
                        'domain': [1, 2, 3, 4, 5, 6, 7, 8],
                        'force': [3, 8]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'size',
                        'sorted': True,
                        'domain': [50, 100, 500, 3000],
                        'force': [100, 3000]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'removeStopWords',
                        'domain': [True, False],
                        # 'force': [False]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'removePunct',
                        'domain': [True, False],
                        'force': [False]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'toLowerCase',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'lemma',
                        'domain': [True, False],
                        # 'force': [True]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'dataPart',
                        'sorted': True,
                        'domain': [0.1, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0],
                        'force': [1.0]
                    },
                ]
            }
        ]
    },
    {
        'name': 'RandomFeature',
        'domain': [True, False],
        'disabled': True,
        'force': [False]
    },
    {
        'name': 'MultiDoc2VecFeature',
        'domain': [True, False],
        'force': [True],
        'disabled': True,
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'd2vSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0],
                        # 'force': [0.0, 0.5, 1.0],
                        'force': [0.0],
                        
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            },
            {
                'constraints': [[True]],
                'name': 'fileIdSet',
                'domain':
                [
                    [
                        "_s500000_w3_mc200_lemma_nostopword_nopunct_lowercase_brown",
                        "_s500000_w5_mc7_lemma_nostopword_nopunct_lowercase_brown",
                        "_s10000_w8_mc20_lemma_nostopword_nopunct_lowercase_brown",
                        "_s500000_w30_mc7_lemma_nostopword_nopunct_lowercase_brown",
                        "_s10_w20_mc20_lemma_nostopword_nopunct_lowercase_brown",
                        "_s50_w30_mc200_lemma_nostopword_nopunct_lowercase_brown",
                        "_s50_w8_mc4_lemma_nostopword_nopunct_lowercase_brown",
                        "_s300_w3_mc20_lemma_nostopword_nopunct_lowercase_brown",
                    ]
                ]
            }
        ]
    },
    {
        'name': 'Doc2VecFeature',
        'domain': [True, False],
        'force': [True],
        'disabled': False,
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'data',
                'domain': ['ukwac', 'enwiki', 'ukwac_enwiki', 'halfukwac', 'brown', 'stsall'],
                # 'force': ['brown', 'stsall'],
                # 'force': ['ukwac'],
                'force': ['brown'],
                'subparams':
                [
                    {
                        'name': 'sample',
                        'sorted': True,
                        'default': 0.0,
                        'domain': [0.0, 1e-5],
                        # 'force': np.arange(0.00034, 0.00037, 0.000001)
#     print np.arange(0.00000, 0.000015, 0.000002)
#     print np.arange(0.000015, 0.000030, 0.000002)
#     print np.arange(0.000030, 0.000045, 0.000002)
#     print np.arange(0.000045, 0.000060, 0.000002)
#     print np.arange(0.000060, 0.000075, 0.000002)
#     print np.arange(0.000075, 0.000090, 0.000002)
#     print np.arange(0.000090, 0.000105, 0.000002)
#     print np.arange(0.000105, 0.000120, 0.000002)
#     print np.arange(0.000120, 0.000135, 0.000002)
#     print np.arange(0.000135, 0.000150, 0.000002)
                        # 'force': [0.00006, 0.0001, 0.00008, 0.00012]
                        # 'force': [0.00006, 0.0001]
                        
#                         'force': list(np.arange(0.00003, 0.00012, 0.000001))
                        'force': [6.8e-05]
                    },
                    {
                        'name': 'iter',
                        'sorted': True,
                        'default': 5,
                        'domain': range(1, 20, 1),
                        'force': [22]
                    },
                    {
                        'name': 'negative',
                        'sorted': True,
                        'default': 0,
                        'domain': range(5, 20, 1),
                        'force': [0]
                    },
                    {
                        'name': 'alpha',
                        'default': 0.025,
                        'sorted': True,
                        'domain': [0.005, 0.010, 0.015, 0.020, 0.025, 0.030, 0.035, 0.040, 0.045],
                        # 'force': [5, 15]
#                         'force': [0.045, 0.7, 0.8, 0.9, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.2, 0.3, 0.4, 0.5]
#                         'force': [0.045, 0.1, 0.2, 0.3, 0.4, 0.5]
#                         'force': np.arange(0.07, 0.15, 0.01)
                        #'force': [0.06, 0.08, 0.09, 0.1]
                        'force': [0.08]
                    },
                    {
                        'name': 'min_count',
                        'sorted': True,
                        'domain': [0, 1, 3, 7, 15, 200],
                        # 'force': [5, 15]
                        'force': [0]
                    },
                    {
                        'name': 'window',
                        'sorted': True,
                        'domain': [1, 2, 3, 4, 5, 6, 7, 8],
                        # 'force': [1, 2, 3, 8]
                        'force': [1, 2, 3, 5, 8]
                    },
                    {
                        'name': 'size',
                        'sorted': True,
                        'domain': [50, 100, 500, 3000],
                        # 'force': [50, 80, 100, 120, 200, 300, 500, 1000, 3000, 6000]
                        # 'force': [50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 180, 190, 200]
                        'force': [150]
                    },
                    { 
                        'name': 'removeStopWords',
                        'domain': [True, False],
                        # 'force': [False]
                    },
                    {
                        'name': 'removePunct',
                        'domain': [True, False],
                        # 'force': [False]
                    },
                    {
                        'name': 'toLowerCase',
                        'domain': [True, False],
                        # 'force': [True]
                    },
                    {
                        'name': 'lemma',
                        'domain': [True, False],
                        # 'force': [True]
                    },
                    {
                        'name': 'dataPart',
                        'sorted': True,
                        'domain': [0.1, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0],
                        # 'force': [0.0, 0.25, 0.5, 0.75, 1.0]
                        # 'force': [0.0, 0.5, 1.0]
                        # 'force': [0.0, 1.0]
                        # 'force': [0.0, 0.5, 1.0]
                        'force': [1.0]
                    },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'd2vSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0],
                        # 'force': [0.0, 0.5, 1.0],
                        'force': [0.0],
                        
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            }
        ]
    }
]

###############################################################################
############################# randomFolderd2vBrownCombsDef ################################
###############################################################################

randomFolderd2vBrownCombsDef = \
[
    {
        'name': 'score',
        'domain': ['MeanLeastSquares', 'MeanDifference', 'ScipyPearsonCorrelation', 'NumpyPearsonCorrelation', 'AgirrePearsonCorrelation'],
        'force': ['NumpyPearsonCorrelation']
    },
    {
        'name': 'regressor',
        'domain': ['KernelRidge', 'LinearRegression', 'Ridge', 'RidgeCV', 'Lasso', 'ElasticNet', 'LinearSVR', 'SVR', 'NuSVR'],
        'force': ['Ridge'],
        # 'force': ['LinearSVR', 'SVR', 'NuSVR'],
        'subparams':
        [
            {
                'constraints': [['Ridge', 'RidgeCV', 'Lasso', 'ElasticNet', 'KernelRidge']],
                'name': 'alpha',
                'domain': list(np.arange(0.1, 3.0, 0.1)),
                'force': [2.7]
            },
            {
                'constraints': [['ElasticNet']],
                'name': 'l1_ratio',
                'domain': list(np.arange(0.0, 1.0, 0.1)),
                'force': [0.5]
            },
            {
                'constraints': [['SVR', 'LinearSVR']],
                'name': 'epsilon',
                'domain': [0.03, 0.06, 0.1, 0.13, 0.16, 0.2],
                'force': [0.1]
            },
            {
                'constraints': [['NuSVR']],
                'name': 'nu',
                'domain': list(np.arange(0.1, 1.0, 0.1)),
                'force': [0.5]
            },
            {
                'constraints': [['SVR', 'NuSVR', 'LinearSVR']],
                'name': 'C',
                'domain': [0.1, 0.5, 1.0, 1.5, 2.0],
                'force': [1.0]
            },
            {
                'constraints': [['SVR', 'NuSVR']],
                'name': 'shrinking',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [['LinearSVR']],
                'name': 'dual',
                'domain': [True, False],
                'force': [False]
            },
            {
                'constraints': [['SVR', 'NuSVR', 'KernelRidge']],
                'name': 'kernel',
                'domain': ['linear', 'poly', 'rbf', 'sigmoid', 'precomputed'],
                'force': ['rbf'],
                'subparams':
                [
                    {
                        'constraints': [['poly']],
                        'name': 'degree',
                        'domain': [1, 2, 3, 4, 5, 6],
                        'force': [3]
                    },
                    {
                        'constraints': [['poly', 'rbf', 'sigmoid']],
                        'name': 'gamma',
                        'domain': [0.03, 0.06, 0.1, 0.13, 0.16, 0.2],
                        'force': [0.1]
                    },
                    {
                        'constraints': [['poly', 'sigmoid']],
                        'name': 'coef0',
                        'domain': list(np.arange(0.0, 1.0, 0.1)),
                        'force': [0.0]
                    }
                ]
            }
        ]
    },
    {
        'name': 'data',
        'domain': ['SamsungPolandMappingSets2016', 'NormalSets2016', 'NormalSets2015', 'Normal2012', 'Normal2015', 'Normal2016', 'CrossValidation2015', 'CrossValidation2016', 'CrossValidation2017'],
        'disabled': False,
        'force': ['CrossValidation2016'],
        'subparams':
        [
            {
                'constraints': [['CrossValidation2015', 'CrossValidation2016', 'CrossValidation2017']],
                'name': 'partsCount',
                'domain': [3, 5, 10, 20],
                'force': [10]
            }
        ]
    },
    {
        'name': 'agParser',
        'domain': [True],
        'subparams':
        [
            {
                'name': 'removeStopWords',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'removePunct',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'toLowerCase',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'lemma',
                'domain': [True, False],
                'force': [False]
            }
        ]
    },
    {
        'name': 'LengthFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [True],
        'subparams':
        [
            {
                'name': 'string',
                'domain': [True, False],
                'force': [True]
            },
            {
                'name': 'tokens',
                'domain': [True, False],
                'force': [True]
            }
        ]
    },
    {
        'name': 'SentencePairFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [False],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'sameUpperCaseCount',
                'domain': [True, False],
                'force': [False]
            },
            {
                'constraints': [[True]],
                'name': 'sameLemmaCount',
                'domain': [True, False],
                'force': [True]
            },
            {
                'constraints': [[True]],
                'name': 'word',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'stringLength', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'substraction', 'domain': [True, False], 'force': [True] },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'punct',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'stopword',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    { 'constraints': [[True]], 'name': 'smallsw3', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'bigsw1', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'nltksw', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'tokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'swTokenCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'stringLength', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'sameCount', 'domain': [True, False], 'force': [True] },
                    { 'constraints': [[True]], 'name': 'substraction', 'domain': [True, False], 'force': [True] },
                ]
            },
        ]
    },
    {
        'name': 'SultanAlignerFeature',
        'domain': [True, False],
        'disabled': False,
        'force': [False],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'similarity1',
                'domain': [True, False],
                'force': [True],
            },
            {
                'constraints': [[True]],
                'name': 'similarity2',
                'domain': [True, False],
                'force': [True],
            }
        ]
    },
    {
        'name': 'Word2VecFeature',
        'domain': [True, False],
        'disabled': True,
        'force': [True],
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'homeMadeSimilarity',
                'domain': [True, False],
                'force': [False],
            },
            {
                'constraints': [[True]],
                'name': 'w2vNSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0], # best 0.0 pour brown_stsall et 1.0 pour GoogleNews
                        'force': [0.0]
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            },
            { 
                'constraints': [[True]],
                'name': 'data',
                'domain': ['brown_stsall', 'brown', 'stsall', 'BaroniVectors', 'GoogleNews'],
                'force': ['brown_stsall'], # best GoogleNews then brown_stsall
                'subparams':
                [
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'min_count',
                        'sorted': True,
                        'domain': [0, 1, 3, 7, 15, 200],
                        # 'force': [5, 15]
                        'force': [0]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'window',
                        'sorted': True,
                        'domain': [1, 2, 3, 4, 5, 6, 7, 8],
                        'force': [3, 8]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'size',
                        'sorted': True,
                        'domain': [50, 100, 500, 3000],
                        'force': [100, 3000]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'removeStopWords',
                        'domain': [True, False],
                        # 'force': [False]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'removePunct',
                        'domain': [True, False],
                        'force': [False]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'toLowerCase',
                        'domain': [True, False],
                        'force': [True]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'lemma',
                        'domain': [True, False],
                        # 'force': [True]
                    },
                    {
                        'constraints': [['brown_stsall', 'brown', 'stsall']],
                        'name': 'dataPart',
                        'sorted': True,
                        'domain': [0.1, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0],
                        'force': [1.0]
                    },
                ]
            }
        ]
    },
    {
        'name': 'RandomFeature',
        'domain': [True, False],
        'disabled': True,
        'force': [False]
    },
    {
        'name': 'MultiDoc2VecFeature',
        'domain': [True, False],
        'force': [True],
        'disabled': True,
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'd2vSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0],
                        # 'force': [0.0, 0.5, 1.0],
                        'force': [0.0],
                        
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            },
            {
                'constraints': [[True]],
                'name': 'fileIdSet',
                'domain':
                [
                    [
                        "_s500000_w3_mc200_lemma_nostopword_nopunct_lowercase_brown",
                        "_s500000_w5_mc7_lemma_nostopword_nopunct_lowercase_brown",
                        "_s10000_w8_mc20_lemma_nostopword_nopunct_lowercase_brown",
                        "_s500000_w30_mc7_lemma_nostopword_nopunct_lowercase_brown",
                        "_s10_w20_mc20_lemma_nostopword_nopunct_lowercase_brown",
                        "_s50_w30_mc200_lemma_nostopword_nopunct_lowercase_brown",
                        "_s50_w8_mc4_lemma_nostopword_nopunct_lowercase_brown",
                        "_s300_w3_mc20_lemma_nostopword_nopunct_lowercase_brown",
                    ]
                ]
            }
        ]
    },
    {
        'name': 'Doc2VecFeature',
        'domain': [True, False],
        'force': [True],
        'disabled': False,
        'subparams':
        [
            {
                'constraints': [[True]],
                'name': 'data',
                'domain': ['ukwac', 'enwiki', 'ukwac_enwiki', 'halfukwac', 'brown', 'stsall'],
                # 'force': ['brown', 'stsall'],
                # 'force': ['ukwac'],
                'force': ['brown'],
                'subparams':
                [
                    {
                        'name': 'sample',
                        'sorted': True,
                        'default': 0.0,
                        'domain': [0.0, 1e-5],
                        # 'force': np.arange(0.00034, 0.00037, 0.000001)
#     print np.arange(0.00000, 0.000015, 0.000002)
#     print np.arange(0.000015, 0.000030, 0.000002)
#     print np.arange(0.000030, 0.000045, 0.000002)
#     print np.arange(0.000045, 0.000060, 0.000002)
#     print np.arange(0.000060, 0.000075, 0.000002)
#     print np.arange(0.000075, 0.000090, 0.000002)
#     print np.arange(0.000090, 0.000105, 0.000002)
#     print np.arange(0.000105, 0.000120, 0.000002)
#     print np.arange(0.000120, 0.000135, 0.000002)
#     print np.arange(0.000135, 0.000150, 0.000002)
                        # 'force': [0.00006, 0.0001, 0.00008, 0.00012]
                        # 'force': [0.00006, 0.0001]
                        
#                         'force': list(np.arange(0.00003, 0.00012, 0.000001))
                        'force': [6.8e-05]
                    },
                    {
                        'name': 'iter',
                        'sorted': True,
                        'default': 5,
                        'domain': range(1, 20, 1),
                        'force': [22]
                    },
                    {
                        'name': 'negative',
                        'sorted': True,
                        'default': 0,
                        'domain': range(5, 20, 1),
                        'force': [0]
                    },
                    {
                        'name': 'alpha',
                        'default': 0.025,
                        'sorted': True,
                        'domain': [0.005, 0.010, 0.015, 0.020, 0.025, 0.030, 0.035, 0.040, 0.045],
                        # 'force': [5, 15]
#                         'force': [0.045, 0.7, 0.8, 0.9, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.2, 0.3, 0.4, 0.5]
#                         'force': [0.045, 0.1, 0.2, 0.3, 0.4, 0.5]
#                         'force': np.arange(0.07, 0.15, 0.01)
                        #'force': [0.06, 0.08, 0.09, 0.1]
                        'force': [0.08]
                    },
                    {
                        'name': 'min_count',
                        'sorted': True,
                        'domain': [0, 1, 3, 7, 15, 200],
                        # 'force': [5, 15]
                        'force': [0]
                    },
                    {
                        'name': 'window',
                        'sorted': True,
                        'domain': [1, 2, 3, 4, 5, 6, 7, 8],
                        # 'force': [1, 2, 3, 8]
                        'force': [1, 2, 3, 5, 8]
                    },
                    {
                        'name': 'size',
                        'sorted': True,
                        'domain': [50, 100, 500, 3000],
                        # 'force': [50, 80, 100, 120, 200, 300, 500, 1000, 3000, 6000]
                        # 'force': [50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 180, 190, 200]
                        'force': [100]
                    },
                    { 
                        'name': 'removeStopWords',
                        'domain': [True, False],
                        # 'force': [False]
                    },
                    {
                        'name': 'removePunct',
                        'domain': [True, False],
                        # 'force': [False]
                    },
                    {
                        'name': 'toLowerCase',
                        'domain': [True, False],
                        # 'force': [True]
                    },
                    {
                        'name': 'lemma',
                        'domain': [True, False],
                        # 'force': [True]
                    },
                    {
                        'name': 'dataPart',
                        'sorted': True,
                        'domain': [0.1, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0],
                        # 'force': [0.0, 0.25, 0.5, 0.75, 1.0]
                        # 'force': [0.0, 0.5, 1.0]
                        # 'force': [0.0, 1.0]
                        # 'force': [0.0, 0.5, 1.0]
                        'force': [1.0]
                    },
                ]
            },
            {
                'constraints': [[True]],
                'name': 'd2vSimilarity',
                'domain': [True, False],
                'force': [True],
                'subparams':
                [
                    {
                        'constraints': [[True]],
                        'name': 'defaultSimilarity',
                        'domain': [0.0, 0.2, 0.5, 0.8, 1.0],
                        # 'force': [0.0, 0.5, 1.0],
                        'force': [0.0],
                        
                    }
                ]
            },
            {
                'constraints': [[True]],
                'name': 'vector',
                'domain': [True, False],
                'force': [False],
            }
        ]
    }
]