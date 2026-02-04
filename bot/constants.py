SEARCH_QUERIES = {
    "concerts": [
        "Metallica full concert",
        "Metallica complete live show",
        "Metallica entire performance",
        "Metallica full setlist live",
        "Metallica concert full video",
        "Metallica live at full show",
        "Metallica World Tour complete",
        "Metallica Stadium full concert",
        "Metallica complete show",
        "Metallica full live concert"
    ],
    "interviews": [
        "Metallica full interview",
        "Metallica complete interview",
        "Metallica long form interview",
        "Metallica in-depth interview",
        "Metallica conversation full",
        "Metallica interview session complete",
        "Metallica James Hetfield interview",
        "Metallica Lars Ulrich interview",
        "Metallica band interview full",
        "Metallica exclusive interview"
    ]
}

EXCLUDE_KEYWORDS = [
    "part 1", "part 2", "part 3", "part 4", "part 5",
    "clip", "sample", "preview", "trailer",
    "medley", "cover", "tribute",
    "teaser", "announcement",
    "guitar lesson", "drum cover",
    "bass cover", "drummed", "instrumental",
    "reaction", "review", "analysis",
    "behind the scenes", "making of",
    "music video", "official video"
]

QUALITY_INDICATORS = {
    "official": ["official", "official video", "official bootleg"],
    "hd": ["720p", "1080p", "hd", "high definition", "4k", "uhd"],
    "audio": ["audio only", "soundboard", "flac", "lossless"],
    "complete": ["full", "complete", "entire", "whole", "full show", "full concert"]
}

CONTENT_TYPE_CONCERT = "concert"
CONTENT_TYPE_INTERVIEW = "interview"

QUALITY_SCORE_THRESHOLDS = {
    "HD": 60,
    "OFFICIAL": 70,
    "COMPLETE": 50
}

RESULTS_PER_PAGE = 10
