## Temperature-based Clustering Summary

### Cluster sizes
- Low-temperature optimal: 20
- Mid-temperature optimal: 10
- High-temperature optimal: 4
- Temperature-robust: 32
- Temperature-sensitive: 0

### Criteria
- Low-temperature optimal: Best accuracy at T<=0.2 or decreasing trend.
- Mid-temperature optimal: Best accuracy at T in {0.4, 0.6}.
- High-temperature optimal: Best accuracy at T>=0.8 or increasing trend.
- Temperature-robust: Accuracy nearly flat across temperatures (std<=0.015 or range<=0.02).
- Temperature-sensitive: Non-monotonic with notable swings (range>=0.05).

### Per-question overview
Question | Cluster | Best T | Best Acc | Mean | Std | Slope
--- | --- | --- | --- | --- | --- | ---
Is this a religious book? | High-temperature optimal | 1.0 | 0.849 | 0.793 | 0.027 | 0.030
Is this a sci-fi book? | High-temperature optimal | 1.0 | 0.760 | 0.719 | 0.023 | 0.008
Is this book related to Humor & Entertainment? | High-temperature optimal | 1.0 | 0.783 | 0.750 | 0.021 | 0.053
Is this book related to Politics & Social Sciences? | High-temperature optimal | 1.0 | 0.842 | 0.732 | 0.060 | 0.066
Is this a historical book? | Low-temperature optimal | 0.2 | 0.944 | 0.926 | 0.021 | -0.016
Is this a homosexuality book? | Low-temperature optimal | 0.0 | 0.889 | 0.753 | 0.089 | -0.053
Is this a journey related book? | Low-temperature optimal | 0.2 | 0.816 | 0.767 | 0.028 | 0.011
Is this a reference book? | Low-temperature optimal | 0.2 | 0.586 | 0.563 | 0.016 | 0.010
Is this a romantic book? | Low-temperature optimal | 0.0 | 0.849 | 0.823 | 0.027 | 0.004
Is this a sociopolitical book? | Low-temperature optimal | 0.0 | 0.591 | 0.583 | 0.017 | -0.019
Is this a transportation engineering book? | Low-temperature optimal | 0.0 | 0.809 | 0.770 | 0.018 | -0.034
Is this a youngster related book? | Low-temperature optimal | 0.0 | 0.694 | 0.648 | 0.021 | -0.040
Is this an art related book? | Low-temperature optimal | 0.2 | 0.897 | 0.879 | 0.017 | -0.015
Is this book related to Arts & Photography? | Low-temperature optimal | 0.2 | 0.905 | 0.889 | 0.022 | 0.027
Is this book related to Gay & Lesbian? | Low-temperature optimal | 0.0 | 1.000 | 0.949 | 0.036 | -0.066
Is this book related to Medical Books? | Low-temperature optimal | 0.0 | 0.818 | 0.807 | 0.017 | -0.042
Is this book related to Reference? | Low-temperature optimal | 0.2 | 0.600 | 0.550 | 0.058 | -0.043
Is this book related to Religion & Spirituality? | Low-temperature optimal | 0.0 | 0.828 | 0.805 | 0.016 | -0.020
Is this book related to Romance? | Low-temperature optimal | 0.2 | 1.000 | 0.960 | 0.018 | -0.020
Is this book related to Self-Help? | Low-temperature optimal | 0.2 | 0.955 | 0.932 | 0.023 | 0.006
Is this book related to Sports & Outdoors? | Low-temperature optimal | 0.0 | 0.963 | 0.932 | 0.025 | -0.058
Is this book related to Teen & Young Adult? | Low-temperature optimal | 0.0 | 0.870 | 0.830 | 0.038 | -0.084
Is this christianity book? | Low-temperature optimal | 0.2 | 0.878 | 0.833 | 0.030 | -0.011
What is the edition of this book? | Low-temperature optimal | 0.2 | 1.000 | 0.333 | 0.471 | -0.571
Is this a child-care book? | Mid-temperature optimal | 0.6 | 0.905 | 0.873 | 0.022 | 0.027
Is this a comics book? | Mid-temperature optimal | 0.6 | 0.941 | 0.873 | 0.040 | -0.059
Is this a fitness book? | Mid-temperature optimal | 0.4 | 0.588 | 0.562 | 0.018 | -0.000
Is this a games related book? | Mid-temperature optimal | 0.4 | 0.743 | 0.719 | 0.020 | 0.029
Is this a judicial book? | Mid-temperature optimal | 0.4 | 0.818 | 0.788 | 0.028 | -0.000
Is this a motivational book? | Mid-temperature optimal | 0.6 | 0.941 | 0.912 | 0.029 | 0.076
Is this a pedagogy book? | Mid-temperature optimal | 0.6 | 0.900 | 0.817 | 0.037 | 0.014
Is this book related to Crafts, Hobbies & Home? | Mid-temperature optimal | 0.6 | 0.939 | 0.914 | 0.021 | 0.039
Is this book related to Education & Teaching? | Mid-temperature optimal | 0.4 | 0.733 | 0.644 | 0.050 | -0.095
Is this book related to Literature & Fiction? | Mid-temperature optimal | 0.4 | 0.878 | 0.850 | 0.023 | -0.018
Is this a comedy book? | Temperature-robust | 0.6 | 0.581 | 0.569 | 0.009 | 0.010
Is this a crafts or hobbies related book? | Temperature-robust | 1.0 | 0.862 | 0.838 | 0.011 | 0.021
Is this a digital technology book? | Temperature-robust | 0.4 | 0.939 | 0.924 | 0.015 | 0.029
Is this a financial book? | Temperature-robust | 0.0 | 0.588 | 0.583 | 0.011 | -0.021
Is this a kids book? | Temperature-robust | 0.0 | 0.864 | 0.853 | 0.013 | -0.034
Is this a life story book? | Temperature-robust | 0.0 | 0.821 | 0.821 | 0.000 | -0.000
Is this a pharmaceutical book? | Temperature-robust | 1.0 | 0.327 | 0.304 | 0.010 | 0.019
Is this a recipe book? | Temperature-robust | 0.0 | 0.871 | 0.871 | 0.000 | 0.000
Is this an exam preparation book? | Temperature-robust | 0.4 | 0.958 | 0.958 | 0.001 | 0.002
Is this book related to Biographies & Memoirs? | Temperature-robust | 0.0 | 0.917 | 0.917 | 0.000 | 0.000
Is this book related to Business & Money? | Temperature-robust | 0.2 | 0.850 | 0.838 | 0.013 | 0.004
Is this book related to Calendars? | Temperature-robust | 0.0 | 1.000 | 1.000 | 0.000 | 0.000
Is this book related to Children's Books? | Temperature-robust | 0.0 | 0.902 | 0.884 | 0.008 | -0.015
Is this book related to Christian Books & Bibles? | Temperature-robust | 0.2 | 0.954 | 0.938 | 0.011 | 0.007
Is this book related to Comics & Graphic Novels? | Temperature-robust | 0.0 | 1.000 | 1.000 | 0.000 | 0.000
Is this book related to Computers & Technology? | Temperature-robust | 0.0 | 0.976 | 0.976 | 0.000 | 0.000
Is this book related to Cookbooks, Food & Wine? | Temperature-robust | 0.0 | 0.971 | 0.961 | 0.014 | -0.017
Is this book related to Engineering & Transportation? | Temperature-robust | 0.0 | 0.968 | 0.968 | 0.000 | 0.000
Is this book related to Health, Fitness & Dieting? | Temperature-robust | 0.0 | 0.854 | 0.829 | 0.014 | -0.028
Is this book related to History? | Temperature-robust | 0.0 | 0.913 | 0.909 | 0.008 | -0.009
Is this book related to Law? | Temperature-robust | 0.0 | 0.889 | 0.889 | 0.000 | 0.000
Is this book related to Mystery, Thriller & Suspense? | Temperature-robust | 0.0 | 1.000 | 1.000 | 0.000 | 0.000
Is this book related to Parenting & Relationships? | Temperature-robust | 0.0 | 0.824 | 0.824 | 0.000 | -0.000
Is this book related to Science & Math? | Temperature-robust | 0.2 | 0.877 | 0.868 | 0.009 | -0.003
Is this book related to Science Fiction & Fantasy? | Temperature-robust | 0.0 | 1.000 | 1.000 | 0.000 | 0.000
Is this book related to Test Preparation? | Temperature-robust | 0.0 | 0.958 | 0.958 | 0.000 | 0.000
Is this book related to Travel? | Temperature-robust | 0.0 | 0.911 | 0.904 | 0.011 | -0.006
What is the genre of this book? | Temperature-robust | 1.0 | 0.411 | 0.400 | 0.007 | 0.008
What is the title of this book? | Temperature-robust | 0.4 | 0.839 | 0.826 | 0.008 | -0.007
What type of book is this? | Temperature-robust | 0.8 | 0.337 | 0.312 | 0.013 | 0.006
Who is the author of this book? | Temperature-robust | 0.0 | 0.858 | 0.848 | 0.006 | -0.006
Who wrote this book? | Temperature-robust | 0.4 | 0.841 | 0.836 | 0.005 | -0.003
