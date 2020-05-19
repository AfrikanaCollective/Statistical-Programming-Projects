library(data.table)
library(ggplot2)
library(lme4)
library(optimx)
library(ggsci)
library(tidyverse)
library(groupdata2)
library(ggpubr)
library(pROC)
library(caret)
library(foreach)
library(doParallel)
library(extrafont)
library(sjPlot)
library(gridExtra)
library(FSA)
library(knitr)
library(ggalluvial)
library(DescTools)
library(lmerTest)

loadfonts(device="win")
par(family='Corbel')

setwd("D:/Statistical Programming Projects/Experiment")

#Use 400 users with complete sessions
data = data.table(read.csv("long_gain.csv"))
data[Cycle_Complete > 7,Cycle_Complete:=7]
data <- within(data, Group <- relevel(Group, ref = "Control"))

#data[,Gap_Seconds_Log:=log(exp(Gap)*60)] #converts log minutes to log seconds

#https://datascienceplus.com/analysing-longitudinal-data-multilevel-growth-models-ii/
#https://stats.stackexchange.com/questions/31569/questions-about-how-random-effects-are-specified-in-lmer
model <- lmer(Score ~ Group*Gap + Group*Cycle_Complete + (1+Cycle_Complete|User), 
              control = lmerControl(optimizer ="Nelder_Mead"), data=data) #Random intercept at Student, Random slope at occasion
tab_model(model)


