#' Statistical analysis for the online experiment on personalizing news aggregators.
#' The analysis predicts the impact of various personalized profiles on the news diversity of various news websites.
#' 
#' Abstract:  People increasingly use personalizing news aggregators for acquiring news online.
#'     Despite benefits such as more relevance, risks such as filter bubbles have been elicited.
#'     So far, there is little empirical evidence on how personalization affects the news diversity
#'     of news aggregators. Furthermore, it remains unclear how the news diversity of news aggregators
#'     compares to edited newspaper websites. This study investigates the effect of personalization on
#'     news diversity and reports the results of an online experiment. Based on browser instrumentation,
#'     news articles were queried using personalized and non-personalized profiles. Using a fixed-effects
#'     model, the news diversity’s change due to personalization was estimated at 8-12%. However, the
#'     absolute news diversity of the personalizing news aggregators is comparable to edited newspaper
#'     websites with a difference of <5%. Our results contribute empirical insights to the debate on news
#'     personalization, finding that filter bubbles stemming from low news diversity are unlikely.
#' 
#' @author Joschka A. Huellmann <j.huellmann@utwente.nl>
#' @author Leonard W. Sensmeier <l_sens01@uni-muenster.de>
#' @date 2022-05-25
#'

# setwd("C:\\Users\\jhuellmann\\GoogleDrive\\Research\\Tracking\\2021-01-05-leonard-sensmeier-news\\2021-05-27-wi-paper")
setwd("D:\\Google Drive\\Research\\Tracking\\2021-01-05-leonard-sensmeier-news\\2021-05-27-wi-paper")
setwd("C:\\Users\\HullmannJA\\GoogleDrive\\Research\\Tracking\\2021-01-05-leonard-sensmeier-news\\2021-05-27-wi-paper")

library(dplyr)
library(tidyr)
library(vegan)
library(ggplot2)
library(stargazer)
library(xtable)
library(reporttools)
library(plm)
library(lmtest)
library(psych)
library(Hmisc)
library(car)
library(perturb)
source("tableNominal.R") # substitute longtable with tabular, as longtable is not supported by base LaTeX

df <- read.csv("export.csv")
df$sourceDatetime <- as.POSIXlt(df$sourceDatetime, format = "%Y-%m-%d %H:%M:%OS")
df <- df %>% mutate_if(is.character, as.factor)
df <- df %>% unite(website, sourceType, sourceCounter, remove = F)
# create column day-sequence
df$day <- df$sourceDatetime$mday - 28 
df$day[df$day < 1] <- df$day[df$day < 1] + 31


##
## some configuration
##
# flag whether to plot topic or subtopic
flag.subtopic <- "oberthema"
# flag.subtopic <- "unterthema"

## create long format of data by sourceType,
## Todo Check Source Counter
df.grouped <- df %>% group_by(sourceType, get(flag.subtopic)) %>% summarise(n = n()) %>% mutate(freq = n / sum(n)) %>% as.data.frame
colnames(df.grouped)[2] <-  flag.subtopic

##
## 1. desciptive statistics
##
tableNominal((df[,sapply(df, is.factor)]))



##
## 2. plot bar chart
##
ggplot(df.grouped, aes(x=get(flag.subtopic), y=freq, fill=get(flag.source))) +
    geom_bar(stat='identity', position='dodge')



##
## 3a. calculate diversity per website
## 
df.wide <- reshape(select(df.grouped, -freq), idvar = flag.source, timevar = flag.subtopic, direction = "wide")
row.names(df.wide) <- c("flipBoard","googleNews","spiegel","wn")
df.wide[is.na(df.wide)] <- 0
df.wide <- df.wide[-c(1)]

diversity.shannon <- diversity(df.wide)



##
## 3b. Calculate Diversity 
##

df.test <- df %>% select(sourceType, sourceCounter, oberthema) %>% group_by(sourceType, sourceCounter, oberthema) %>% mutate(n = n(), freq = n / sum(n)) %>%
unite(website, sourceType, sourceCounter) %>% distinct() %>% as.data.frame

# filter corona, coz it may bias results
df.test.covid <- df %>% select(sourceType, sourceCounter, oberthema) %>% group_by(sourceType, sourceCounter, oberthema) %>% mutate(n = n(), freq = n / sum(n)) %>%
unite(website, sourceType, sourceCounter) %>% filter(oberthema != "Corona") %>% distinct() %>% as.data.frame

# use subtopic instead of main topic
df.test.unterthema <- df %>% select(sourceType, sourceCounter, unterthema) %>% group_by(sourceType, sourceCounter, unterthema) %>% mutate(n = n(), freq = n / sum(n)) %>%
unite(website, sourceType, sourceCounter) %>% distinct() %>% as.data.frame

get_diversity <- function(df.test, timevar.p = "oberthema") {
  df.wide <- reshape(select(df.test, -freq), idvar = "website", timevar = timevar.p, direction = "wide")

  df.wide[is.na(df.wide)] <- 0
  df.wide <- df.wide[-c(1)]

  diversity.shannon <- diversity(df.wide)
  diversity.shannon.normalized <- diversity.shannon / log(ncol(df.wide))
  diversity.simpson <- diversity(df.wide, index="simpson")  # inverse so 1 is homogenous

  diversity.indices <- cbind.data.frame(unique(df.test$website), diversity.shannon.normalized, diversity.simpson)
  colnames(diversity.indices) <- c("website", "shannon", "simpson")

  df.diversity <- left_join(df, diversity.indices, by="website") %>% select(website, shannon, simpson, sourceType, profil, day) %>% distinct() %>% as.data.frame
  return(df.diversity)
}

df.diversity <- get_diversity(df.test)
df.diversity.corona <- get_diversity(df.test.covid)
df.diversity.subtopic <- get_diversity(df.test.unterthema, "unterthema")


##
## 4. DESCRIPTIVE STATISTICS of DIVERSITY
##

## (0) summary stats and correlation

describe.by(df.diversity, "sourceType")

temp.googleNews <- df.diversity[df.diversity$sourceType == "googleNews","shannon"]
temp.flipBoard <- df.diversity[df.diversity$sourceType == "flipBoard","shannon"]
temp.spiegel <- df.diversity[df.diversity$sourceType == "spiegel","shannon"]
temp.wn <- df.diversity[df.diversity$sourceType == "wn","shannon"]

max.len <- max(length(temp.googleNews), length(temp.flipBoard), length(temp.spiegel), length(temp.wn))

temp.googleNews <- c(temp.googleNews, rep(NA, max.len - length(temp.googleNews)))
temp.flipBoard <- c(temp.flipBoard, rep(NA, max.len - length(temp.flipBoard)))
temp.spiegel <- c(temp.spiegel, rep(NA, max.len - length(temp.spiegel)))
temp.wn <- c(temp.wn, rep(NA, max.len - length(temp.wn)))

temp.df <- cbind(temp.googleNews, temp.flipBoard, temp.spiegel, temp.wn)

round(cor(temp.df, method="pearson"),2)
rcorr(as.matrix(temp.df), type = "pearson")



## (1) violin plots of diversity

ggplot(df.diversity, aes(x=sourceType, y=shannon)) + 
    geom_violin(trim=FALSE) +
    stat_summary(fun.data=mean_sdl, fun.args = list(mult = 1), geom="pointrange", color="red")

ggplot(df.diversity.corona, aes(x=sourceType, y=shannon)) + 
    geom_violin(trim=FALSE) +
    stat_summary(fun.data=mean_sdl, fun.args = list(mult = 1), geom="pointrange", color="red")

ggplot(df.diversity.subtopic, aes(x=sourceType, y=shannon)) + 
    geom_violin(trim=FALSE) +
    stat_summary(fun.data=mean_sdl, fun.args = list(mult = 1), geom="pointrange", color="red")



ggplot(df.diversity, aes(x=sourceType, y=shannon)) + 
    geom_boxplot() +
    stat_summary(fun.data=mean_sdl, fun.args = list(mult = 1), geom="pointrange", color="red")

ggplot(df.diversity, aes(x=sourceType, y=simpson)) + 
    geom_boxplot() +
    stat_summary(fun.data=mean_sdl, fun.args = list(mult = 1), geom="pointrange", color="red")

ggplot(df.diversity.subtopic, aes(x=sourceType, y=simpson)) + 
    geom_boxplot() +
    stat_summary(fun.data=mean_sdl, fun.args = list(mult = 1), geom="pointrange", color="red")



## (2) scatterplot with regression lines by sequence/chronological order

regline.wn <- line(1:12, df.diversity[1:12,c("shannon")])
regline.spiegel <- line(13:24, df.diversity[13:24,c("shannon")])
regline.flipboard <- line(25:52, df.diversity[25:52,c("shannon")])
regline.googlenews <- line(53:72, df.diversity[53:72,c("shannon")])
# regline.all <- line(1:72, df.diversity[1:72,c("shannon")])    # line on all

ggplot(df.diversity, aes(x=seq(1:77), y=shannon, shape=sourceType, color=profil)) +
    geom_point(size=3) +
    # geom_abline(intercept = regline$coef[1], slope = regline$coef[2])
	geom_segment(aes(x = 1, xend = 12, y = regline.wn$coef[1] + 1 * regline.wn$coef[2], yend = regline.wn$coef[1] + regline.wn$coef[2] * 12), size=1) + 
	geom_segment(aes(x = 13, xend = 24, y = regline.spiegel$coef[1] + 13 * regline.spiegel$coef[2], yend = regline.spiegel$coef[1] + regline.spiegel$coef[2] * 24), size=1) + 
	geom_segment(aes(x = 25, xend = 52, y = regline.flipboard$coef[1] + 25* regline.flipboard$coef[2], yend = regline.flipboard$coef[1] + regline.flipboard$coef[2] * 52), size=1) + 
	geom_segment(aes(x = 53, xend = 72, y = regline.googlenews$coef[1] + 53* regline.googlenews$coef[2], yend = regline.googlenews$coef[1] + regline.googlenews$coef[2] * 72), size=1)
	# geom_segment(aes(x = 1, xend = 72, y = regline.all$coef[1] + 1 * regline.all$coef[2], yend = regline.all$coef[1] + regline.all$coef[2] * 72), size=1)



## (3) scatterplot with regression lines by sequence/chronological order CONTROLLING CORONA

regline.wn <- line(1:12, df.diversity.corona[1:12,c("shannon")])
regline.spiegel <- line(13:24, df.diversity.corona[13:24,c("shannon")])
regline.flipboard <- line(25:52, df.diversity.corona[25:52,c("shannon")])
regline.googlenews <- line(53:72, df.diversity.corona[53:72,c("shannon")])
# regline.all <- line(1:72, df.diversity.corona[1:72,c("shannon")])    # line on all

ggplot(df.diversity.corona, aes(x=seq(1:77), y=shannon, shape=sourceType, color=profil)) +
    geom_point(size=3) +
    # geom_abline(intercept = regline$coef[1], slope = regline$coef[2])
  geom_segment(aes(x = 1, xend = 12, y = regline.wn$coef[1] + 1 * regline.wn$coef[2], yend = regline.wn$coef[1] + regline.wn$coef[2] * 12), size=1) + 
  geom_segment(aes(x = 13, xend = 24, y = regline.spiegel$coef[1] + 13 * regline.spiegel$coef[2], yend = regline.spiegel$coef[1] + regline.spiegel$coef[2] * 24), size=1) + 
  geom_segment(aes(x = 25, xend = 52, y = regline.flipboard$coef[1] + 25* regline.flipboard$coef[2], yend = regline.flipboard$coef[1] + regline.flipboard$coef[2] * 52), size=1) + 
  geom_segment(aes(x = 53, xend = 72, y = regline.googlenews$coef[1] + 53* regline.googlenews$coef[2], yend = regline.googlenews$coef[1] + regline.googlenews$coef[2] * 72), size=1)
  # geom_segment(aes(x = 1, xend = 72, y = regline.all$coef[1] + 1 * regline.all$coef[2], yend = regline.all$coef[1] + regline.all$coef[2] * 72), size=1)



## (4) scatterplot with regression lines by sequence/chronological order CONTROLLING SIMPSON

regline.wn <- line(1:12, df.diversity[1:12,c("simpson")])
regline.spiegel <- line(13:24, df.diversity[13:24,c("simpson")])
regline.flipboard <- line(25:52, df.diversity[25:52,c("simpson")])
regline.googlenews <- line(53:72, df.diversity[53:72,c("simpson")])
# regline.all <- line(1:72, df.diversity[1:72,c("simpson")])    # line on all

ggplot(df.diversity, aes(x=seq(1:77), y=simpson, shape=sourceType, color=profil)) +
    geom_point(size=3) +
    # geom_abline(intercept = regline$coef[1], slope = regline$coef[2])
	geom_segment(aes(x = 1, xend = 12, y = regline.wn$coef[1] + 1 * regline.wn$coef[2], yend = regline.wn$coef[1] + regline.wn$coef[2] * 12), size=1) + 
	geom_segment(aes(x = 13, xend = 24, y = regline.spiegel$coef[1] + 13 * regline.spiegel$coef[2], yend = regline.spiegel$coef[1] + regline.spiegel$coef[2] * 24), size=1) + 
	geom_segment(aes(x = 25, xend = 52, y = regline.flipboard$coef[1] + 25* regline.flipboard$coef[2], yend = regline.flipboard$coef[1] + regline.flipboard$coef[2] * 52), size=1) + 
	geom_segment(aes(x = 53, xend = 72, y = regline.googlenews$coef[1] + 53* regline.googlenews$coef[2], yend = regline.googlenews$coef[1] + regline.googlenews$coef[2] * 72), size=1)
	# geom_segment(aes(x = 1, xend = 72, y = regline.all$coef[1] + 1 * regline.all$coef[2], yend = regline.all$coef[1] + regline.all$coef[2] * 72), size=1)



## (5) scatterplot with regression lines by sequence/chronological order CONTROLLING SUBTOPIC

regline.wn <- line(1:12, df.diversity.subtopic[1:12,c("simpson")])
regline.spiegel <- line(13:24, df.diversity.subtopic[13:24,c("simpson")])
regline.flipboard <- line(25:52, df.diversity.subtopic[25:52,c("simpson")])
regline.googlenews <- line(53:72, df.diversity.subtopic[53:72,c("simpson")])
# regline.all <- line(1:72, df.diversity.subtopic[1:72,c("simpson")])    # line on all

ggplot(df.diversity.subtopic, aes(x=seq(1:77), y=simpson, shape=sourceType, color=profil)) +
    geom_point(size=3) +
    # geom_abline(intercept = regline$coef[1], slope = regline$coef[2])
  geom_segment(aes(x = 1, xend = 12, y = regline.wn$coef[1] + 1 * regline.wn$coef[2], yend = regline.wn$coef[1] + regline.wn$coef[2] * 12), size=1) + 
  geom_segment(aes(x = 13, xend = 24, y = regline.spiegel$coef[1] + 13 * regline.spiegel$coef[2], yend = regline.spiegel$coef[1] + regline.spiegel$coef[2] * 24), size=1) + 
  geom_segment(aes(x = 25, xend = 52, y = regline.flipboard$coef[1] + 25* regline.flipboard$coef[2], yend = regline.flipboard$coef[1] + regline.flipboard$coef[2] * 52), size=1) + 
  geom_segment(aes(x = 53, xend = 72, y = regline.googlenews$coef[1] + 53* regline.googlenews$coef[2], yend = regline.googlenews$coef[1] + regline.googlenews$coef[2] * 72), size=1)
  # geom_segment(aes(x = 1, xend = 72, y = regline.all$coef[1] + 1 * regline.all$coef[2], yend = regline.all$coef[1] + regline.all$coef[2] * 72), size=1)





##
## 5. ANALYSES
##

### (5.1) PROFILES

### some visuals

test <- df.diversity[df.diversity$sourceType %in% c("googleNews","wn", "spiegel"),]
ggplot(data=test, aes(x=day, y=shannon, group=profil, color=profil)) +
  geom_line()+
  geom_point()

test <- df.diversity[df.diversity$sourceType %in% c("googleNews","wn", "spiegel"),]
ggplot(data=test, aes(x=day, y=simpson, group=profil, color=profil)) +
  geom_line()+
  geom_point()

test <- df.diversity[df.diversity$sourceType %in% c("spiegel", "wn"),]
ggplot(data=test, aes(x=day, y=shannon, group=sourceType, color=sourceType)) +
  geom_line()+
  geom_point()

## some tests
test <- df.diversity[df.diversity$sourceType %in% c("googleNews"),]
ggplot(data=test, aes(x=day, y=shannon, group=profil, color=profil)) +
  geom_line()+
  geom_point()







## 6. POWERPOINT / PAPER CALCS

### (1) all from google: baseline profile vs. no baseline
test <- df.diversity[df.diversity$sourceType == "googleNews",]
test <- test[test$day < 5,] # bei google war nen bug
test <- test %>% mutate(baseline = profil == "vprofilgoogle")

summary(lm(shannon ~ baseline, data=test))
summary(lm(shannon ~ baseline + day, data=test))
summary(lm(shannon ~ baseline + as.factor(day), data=test))
summary(lm(shannon ~ baseline + as.factor(day) -1, data=test))
summary(lm(shannon ~ baseline + day + day*baseline, data=test))
summary(lm(shannon ~ baseline + as.factor(day) + as.factor(day)*baseline -1, data=test))


# look at days specifically
summary(lm(shannon ~ day, data=test[test$baseline,]))
summary(lm(shannon ~ day, data=test[!test$baseline,]))


# t.test to check
summary(aov(shannon ~ as.factor(baseline), data=test))
TukeyHSD(aov(shannon ~ as.factor(baseline), data=test))

t.test(shannon ~ baseline, data=test)



### (2) all from google: without baseline vs. all from wn/spiegel
test <- df.diversity[df.diversity$sourceType %in% c("googleNews","wn","spiegel") & df.diversity$profil != "vprofilgoogle",]
test <- test[test$day < 5 | (test$sourceType != "googleNews"),] # bei google war nen bug

summary(lm(shannon ~ sourceType, data=test))
summary(lm(shannon ~ sourceType -1, data=test))
summary(lm(shannon ~ sourceType + day -1, data=test))
summary(lm(shannon ~ sourceType + as.factor(day) -1, data=test))

summary(lm(shannon ~ day, data=test))
summary(lm(shannon ~ as.factor(day) -1, data=test))

summary(aov(shannon ~ as.factor(sourceType), data=test))
TukeyHSD(aov(shannon ~ as.factor(sourceType), data=test))

# t.tests to check
test.spiegel <- test[test$sourceType != "wn",]
test.wn <- test[test$sourceType != "spiegel",]
t.test(shannon ~ sourceType, data=test.spiegel)
t.test(shannon ~ sourceType, data=test.wn)




### (3) all from flipboard: baseline profile vs. no baseline
test <- df.diversity[df.diversity$sourceType == "flipBoard",]
test <- test %>% mutate(baseline = profil == "vprofilflip")

summary(lm(shannon ~ baseline, data=test))
summary(lm(shannon ~ baseline + day, data=test))
summary(lm(shannon ~ baseline + as.factor(day) -1, data=test))
summary(lm(shannon ~ baseline + day + day*baseline, data=test))
summary(lm(shannon ~ baseline + as.factor(day) + as.factor(day)*baseline -1, data=test))



### look at days specifically
summary(lm(shannon ~ day, data=test[test$baseline,]))
summary(lm(shannon ~ day, data=test[!test$baseline,]))


# t.test to check
summary(aov(shannon ~ as.factor(baseline), data=test))
TukeyHSD(aov(shannon ~ as.factor(baseline), data=test))

t.test(shannon ~ baseline, data=test)


### (4) all from flipBoard: without baseline vs. all from wn/spiegel
test <- df.diversity[df.diversity$sourceType %in% c("flipBoard","wn","spiegel") & df.diversity$profil != "vprofilflip",]

summary(lm(shannon ~ sourceType, data=test))
summary(lm(shannon ~ sourceType + day -1, data=test))
summary(lm(shannon ~ sourceType + as.factor(day) -1, data=test))

summary(lm(shannon ~ day, data=test))

summary(aov(shannon ~ as.factor(sourceType), data=test))
TukeyHSD(aov(shannon ~ as.factor(sourceType), data=test))

# t.tests to check
test.spiegel <- test[test$sourceType != "wn",]
test.wn <- test[test$sourceType != "spiegel",]
t.test(shannon ~ sourceType, data=test.spiegel)
t.test(shannon ~ sourceType, data=test.wn)




### (5) all from google without baseline vs all from flipboard without baseline
test <- df.diversity[df.diversity$sourceType %in% c("googleNews","flipBoard") & !(df.diversity$profil %in% c("vprofilflip", "vprofilgoogle")),]
test <- test[test$day < 5 | (test$sourceType != "googleNews"),] # bei google war nen bug

summary(lm(shannon ~ sourceType, data=test))
summary(lm(shannon ~ sourceType -1, data=test))
summary(lm(shannon ~ sourceType + day -1, data=test))
summary(lm(shannon ~ sourceType + as.factor(day) -1, data=test))

summary(lm(shannon ~ day, data=test))

summary(aov(shannon ~ as.factor(sourceType), data=test))
TukeyHSD(aov(shannon ~ as.factor(sourceType), data=test))

t.test(shannon ~ sourceType, data=test)



### (6) full model

# by sourceType
summary(lm(shannon ~ sourceType, data=df.diversity))
summary(lm(shannon ~ sourceType + as.factor(day) -1, data=df.diversity))
summary(lm(shannon ~ sourceType + profil + profil * sourceType, data=df.diversity))
summary(lm(shannon ~ sourceType + profil + profil * sourceType + day -1, data=df.diversity))

# by profile
summary(lm(shannon ~ profil, data=df.diversity))


# using plm

# FE for days
summary(lm(shannon ~ sourceType + factor(day), data=df.diversity))
summary(plm(shannon ~ sourceType, data = df.diversity, model="within", index=c("day")))



## 7. ROBUSTNESS

# simpsons index -> no changes
# without corona -> check percentage values
# with subtopics -> check percentage values
# (some websites have more diverse subtopics than others who stick mostly to main topics)
# 
# fixed effect days, also checked effect for days, which was small coefficient and also insignificant, sometimes significant
#


# interaction effects -> nothing significant
# limitations
#  - recent profiles 7 days learning / 7 days simulation
#  - small sample

# We conducted the Durbin-Watson test, which showed no autocorrelation
# The Breusch-Pagan showed no evidence for homoscedasticity.
# We assume homogeneity of variance.


# assumptions for regression and t-test
# normality
shapiro.test()
# data:  df.diversity$shannon
# W = 0.97619, p-value = 0.1573
# No evidence for non-normal distribution.

# breusch pagan tests
test <- df.diversity[df.diversity$sourceType == "googleNews",]
test <- test[test$day < 5,] # bei google war nen bug
test <- test %>% mutate(baseline = profil == "vprofilgoogle")
bptest(lm(shannon ~ baseline, data=test))
# data:  lm(shannon ~ baseline, data = test)
# BP = 0.071572, df = 1, p-value = 0.7891
durbinWatsonTest(lm(shannon ~ baseline, data=test))
# lag Autocorrelation D-W Statistic p-value
#    1      0.04519935      1.772423   0.656
#  Alternative hypothesis: rho != 0

test <- df.diversity[df.diversity$sourceType == "flipBoard",]
test <- test %>% mutate(baseline = profil == "vprofilflip")
bptest(lm(shannon ~ baseline, data=test))
# data:  lm(shannon ~ baseline, data = test)
# BP = 3.3644, df = 1, p-value = 0.06662
durbinWatsonTest(lm(shannon ~ baseline, data=test))
# lag Autocorrelation D-W Statistic p-value
#   1      -0.2686147      2.515093    0.15
# Alternative hypothesis: rho != 0

bptest(lm(shannon ~ sourceType, data=df.diversity))
# data:  lm(shannon ~ sourceType, data = df.diversity)
# BP = 7.1403, df = 3, p-value = 0.06756
durbinWatsonTest(lm(shannon ~ baseline, data=test))
# lag Autocorrelation D-W Statistic p-value
#   1      -0.2686147      2.515093   0.152
# Alternative hypothesis: rho != 0

# heteroscedasitic robust standard errors
# ... (todo, but not necessary)














###
### RANDOM CALCULATIONS
###
test <- df.diversity[df.diversity$sourceType == "googleNews",]
test <- df.diversity[df.diversity$sourceType == "flipBoard",]
test <- df.diversity[df.diversity$sourceType == "wn",]

## average scores between profiles
test %>% group_by(day) %>% mutate(avg = mean(shannon))%>% as.data.frame

## check development of scores
test %>% arrange(day, profil) %>% as.data.frame
test %>% arrange(profil,day) %>% as.data.frame

plot((test %>% arrange(day, profil) %>% as.data.frame)$shannon)
plot((test %>% arrange(profil,day) %>% as.data.frame)$shannon)
