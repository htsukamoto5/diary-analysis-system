# diary-analysis-system
A tool to analyze tagged diary entries. Work in progress

**Diary Analysis System**
A tool for tagging, classifying, and analyzing personal diary entries.
Overview
The Diary Analysis System lets you define a custom tagging format for your diary, classify the tags that appear throughout your entries, and run analyses on the resulting structured data. 
The system is organized into three phases, each building on the output of the last.

**Phase 1: Classification System Builder**
Before any analysis can happen, you need to define how your diary is structured. Phase 1 walks you through building a configuration file (diary_config.json) that captures:

Tag format: The syntax you use for tags in your diary (e.g. {{{TAGNAME_}}}, [[TAGNAME]]). The system extracts prefix and suffix automatically from your format string.
Case sensitivity: Whether {{{ALICE_}}} and {{{alice_}}} should be treated as the same tag, and if not, how to normalize them.
Entry separators: How diary entries are delimited, either by a structured header (with fields like date, volume, page numbers) or by a simple separator character(s).
Tag categories: The semantic categories your tags belong to (e.g. People, Places, Activities, Emotions), along with optional configuration for parent/child relationships between categories, time-based relationships, and custom attributes.

The builder is interactive and fully reversible: you can edit any section before saving, and reload a saved config to modify it later.
Output: diary_config.json

**Phase 2: Tag Scanner & Classifier (in development)**
Phase 2 takes your diary text and the config from Phase 1 and scans through the full text to find every tag. For each tag found, it asks you to classify it within your category system (e.g. is {{{ALICE_}}} a person? a fictional character? a nickname?). It handles the parent/child relationships defined in Phase 1, so classifying a character automatically links them to the right book or show.
Input: diary text + diary_config.json
Output: diary_classified.json (tags with full classification metadata)

**Phase 3: Analysis Engine (planned)**
Phase 3 loads your classified tag data alongside your diary text and lets you run analyses: e.g. co-occurrence of tags, frequency over time, correlation between categories, and more.
Input: diary text + diary_classified.json
Output: analysis results (format TBD)

**Project Structure**
diary-analysis/
├── class_sys_builder.py     # Phase 1: interactive config builder
├── category_config.py       # CategoryConfig dataclass
├── shared_tag_parser.py     # TagFormatParser: parses and validates tag syntax
├── shared_utils.py          # Shared utilities: ListManager, yes_or_no, etc.
└── diary_config.json        # Example output from Phase 1


**Status**
Phase 1 is largely complete with some known gaps (marked # FIX THIS in the source). Phases 2 and 3 are in design/early development.

**Motivation**
I have kept a journal for the past 10 years and wanted to be able to ask questions about it, such as which people I mention the most, whether mentions of hobbies correlate with mentions of the people involved. Existing tools didn't fit my tagging system, so I am building my own from scratch.
