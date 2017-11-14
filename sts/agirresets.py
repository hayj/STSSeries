# coding: utf-8

allAgirreSets = \
[
    ("msrpar", "train", "2012"),
    ("msrvid", "train", "2012"),
    ("smteuroparl", "train", "2012"),
    ("msrpar", "test", "2012"),
    ("msrvid", "test", "2012"),
    ("smteuroparl", "test", "2012"),
    ("onwn", "test", "2012"),
    ("smtnews", "test", "2012"),
    ("fnwn", "test", "2013"),
    ("headlines", "test", "2013"),
    ("onwn", "test", "2013"),
    ("smt", "test", "2013"),
    ("deft-forum", "test", "2014"),
    ("deft-news", "test", "2014"),
    ("headlines", "test", "2014"),
    ("images", "test", "2014"),
    ("onwn", "test", "2014"),
    ("tweet-news", "test", "2014"),
    ("answers-forum", "test", "2015"),
    ("answers-students", "test", "2015"),
    ("belief", "test", "2015"),
    ("headlines", "test", "2015"),
    ("images", "test", "2015"),
    ("answer-answer", "test", "2016"),
    ("headlines", "test", "2016"),
    ("plagiarism", "test", "2016"),
    ("postediting", "test", "2016"),
    ("question-question", "test", "2016"),
]

agirreSets2015 = allAgirreSets[:17]
for current in agirreSets2015:
    assert "2015" not in current
    assert "2016" not in current

allMapping2015 = \
[
    {
        "fileDesc": ("answers-forum", "test", "2015"),
        "resultId": "Ans.-Forum"
    },
    {
        "fileDesc": ("answers-students", "test", "2015"),
        "resultId": "Ans.-Stud."
    },
    {
        "fileDesc": ("belief", "test", "2015"),
        "resultId": "Belief"
    },
    {
        "fileDesc": ("headlines", "test", "2015"),
        "resultId": "HDL"
    },
    {
        "fileDesc": ("images", "test", "2015"),
        "resultId": "Images"
    },
]

allPastAnnotation2015 = \
[
    ("msrpar", "train", "2012"),
    ("msrvid", "train", "2012"),
    ("smteuroparl", "train", "2012"),
    ("msrpar", "test", "2012"),
    ("msrvid", "test", "2012"),
    ("smteuroparl", "test", "2012"),
    ("onwn", "test", "2012"),
    ("smtnews", "test", "2012"),
    ("fnwn", "test", "2013"),
    ("headlines", "test", "2013"),
    ("onwn", "test", "2013"),
    ("smt", "test", "2013"),
    ("deft-forum", "test", "2014"),
    ("deft-news", "test", "2014"),
    ("headlines", "test", "2014"),
    ("images", "test", "2014"),
    ("onwn", "test", "2014"),
    ("tweet-news", "test", "2014"),
]

DLSMapping2015 = \
[
    {
        "fileDesc": ("answers-forum", "test", "2015"),
        "resultId": "Ans.-Forum",
        "trainSet": allPastAnnotation2015
    },
    {
        "fileDesc": ("answers-students", "test", "2015"),
        "resultId": "Ans.-Stud.",
        "trainSet": allPastAnnotation2015
    },
    {
        "fileDesc": ("belief", "test", "2015"),
        "resultId": "Belief",
        "trainSet": allPastAnnotation2015
    },
    {
        "fileDesc": ("headlines", "test", "2015"),
        "resultId": "HDL",
        "trainSet": [("headlines", "test", "2013"),
                     ("headlines", "test", "2014"),
                     ("deft-news", "test", "2014"),
                     ("smtnews", "test", "2012"),]
    },
    {
        "fileDesc": ("images", "test", "2015"),
        "resultId": "Images",
        "trainSet": [("msrpar", "train", "2012"),
                     ("msrpar", "test", "2012"),
                     ("msrvid", "train", "2012"),
                     ("msrvid", "test", "2012"),
                     ("images", "test", "2014"),]
    },
]

samsungPolandMapping2016 = \
[
    {
        "fileDesc": ("answer-answer", "test", "2016"),
        "resultId": "Ans.-Ans.",
        "trainSet": [("answers-students", "test", "2015"),
                     ("belief", "test", "2015")]
#         "trainSet": allPastAnnotation2015
    },
    {
        "fileDesc": ("headlines", "test", "2016"),
        "resultId": "HDL.",
        "trainSet": [("msrpar", "test", "2012"),
                     ("msrpar", "train", "2012"),
                     ("smtnews", "test", "2012"),
                     ("deft-news", "test", "2014"),
                     ("headlines", "test", "2013"),
                     ("headlines", "test", "2014"),
                     ("headlines", "test", "2015"),
                     ("images", "test", "2014"),
                     ("images", "test", "2015")]
    },
    {
        "fileDesc": ("plagiarism", "test", "2016"),
        "resultId": "Plagiarism.",
        "trainSet": [("msrpar", "test", "2012"),
                     ("msrpar", "train", "2012"),
                     ("answers-students", "test", "2015")]
    },
    {
        "fileDesc": ("postediting", "test", "2016"),
        "resultId": "Postediting.",
        "trainSet": [("deft-news", "test", "2014"),
                     ("deft-forum", "test", "2014"),
                     ("smtnews", "test", "2012")]
    },
    {
        "fileDesc": ("question-question", "test", "2016"),
        "resultId": "Ques.-Ques.",
        "trainSet": [("deft-news", "test", "2014"),
                     ("deft-forum", "test", "2014"),
                     ("belief", "test", "2015")]
#         "trainSet": allPastAnnotation2015
    }
]

samsungPolandFeatureAnalysis2016 = \
[
    {
        "BaroniVectorsFeature": True,
        "JacanaAlignFeature": False,
        "MultiDoc2VecFeature.bestTopDelta": False,
        "MultiDoc2VecFeature.fileIdAddOn": False,
        "SultanAlignerFeature": True,
        "Word2VecFeature": True,
    },
    {
        "BaroniVectorsFeature": True,
        "JacanaAlignFeature": True,
        "MultiDoc2VecFeature.bestTopDelta": True,
        "MultiDoc2VecFeature.fileIdAddOn": True,
        "SultanAlignerFeature": True,
        "Word2VecFeature": False,
    },
    {
        "BaroniVectorsFeature": True,
        "JacanaAlignFeature": True,
        "MultiDoc2VecFeature.bestTopDelta": False,
        "MultiDoc2VecFeature.fileIdAddOn": True,
        "SultanAlignerFeature": True,
        "Word2VecFeature": False,
    },
    {
        "BaroniVectorsFeature": True,
        "JacanaAlignFeature": False,
        "MultiDoc2VecFeature.bestTopDelta": False,
        "MultiDoc2VecFeature.fileIdAddOn": True,
        "SultanAlignerFeature": True,
        "Word2VecFeature": False,
    },
    {
        "BaroniVectorsFeature": True,
        "JacanaAlignFeature": True,
        "MultiDoc2VecFeature.bestTopDelta": False,
        "MultiDoc2VecFeature.fileIdAddOn": True,
        "SultanAlignerFeature": True,
        "Word2VecFeature": True,
    }
]

