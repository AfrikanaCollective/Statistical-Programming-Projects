library(ggplot2)
library(extrafont)
library(data.table)
library(nnet)
library(magrittr)
library(caret)
library(sjPlot)
library(mclogit)

loadfonts(device="win")
par(family='Corbel')

setwd("D:/Statistical Programming Projects/Structural Equation Modelling et al")

multinom_regress_data <- as.data.table(read.csv('mutinom_regress_data.csv'))

multinom_regress_data <- within(multinom_regress_data, SRL <- relevel(SRL,ref='High SRL profile'))
multinom_regress_data <- within(multinom_regress_data, Cadre <- relevel(Cadre,ref='Medical Officer'))

multinom_regress_data[Age=='65+',Age:='55+']
multinom_regress_data[Age=='55-64',Age:='55+']
multinom_regress_data[,Age:=factor(as.character(Age))]

multinom_regress_data <- within(multinom_regress_data, Age <- relevel(Age,ref='25-34'))
multinom_regress_data <- within(multinom_regress_data, Level <- relevel(Level,ref='Active Practice(Not training)'))
multinom_regress_data <- within(multinom_regress_data, Platform <- relevel(Platform,ref='LIFE'))

srl_data = multinom_regress_data[!(is.na(User)|User==''),copy(.SD)]
gains_data <- data.table(read.csv("lda.csv"))
agency_data <- merge(srl_data,gains_data,by='User')

multinom_regress_data[,User:=NULL]
multinom_regress_data[,Experience_Scaled:=NULL]

setcolorder(multinom_regress_data,c("SRL","Cadre", "Level", "Age","Experience","Platform"))

multinom_regress_data[,Low:=ifelse(SRL=='Low SRL profile',1,0)]
multinom_regress_data[,Average:=ifelse(SRL=='Average SRL profile',1,0)]
multinom_regress_data[,Above_Average:=ifelse(SRL=='Above Average SRL profile',1,0)]
multinom_regress_data[,High:=ifelse(SRL=='High SRL profile',1,0)]

multinom_regress_data <- within(multinom_regress_data, Platform <- relevel(Platform,ref='LIFE'))

glm.low<-glm(Low~Cadre+Level+Experience+Platform,family=binomial(link='logit'),data=multinom_regress_data)
glm.average<-glm(Average~Cadre+Level+Experience+Platform,family=binomial(link='logit'),data=multinom_regress_data)
glm.above_avg<-glm(Above_Average~Cadre+Level+Experience+Platform,family=binomial(link='logit'),data=multinom_regress_data)
glm.high<-glm(High~Cadre+Level+Experience+Platform,family=binomial(link='logit'),data=multinom_regress_data)
tab_model(glm.low,glm.average,glm.above_avg,glm.high)


repeated_play_data = agency_data[,copy(.SD), 
                                 .SDcols =c("User", "Cadre", "Level", "Experience", "Age", 
                                            "SRL", "Cumilative_Complete_Sessions", "Gain", 
                                            "Experiment")]
repeated_play_data[,Experiment:=factor(Experiment,
                                       levels=c(0:1),
                                       labels=c("Control","Experiment"))]
setnames(repeated_play_data,'Cumilative_Complete_Sessions','Time')
repeated_play_data[,Time:=Time-1]
repeated_play_data[Experience>19,Experience:=20]
repeated_play_data[,Cadre:=factor(as.character(Cadre),
                                  levels=c("Consultant","Medical Officer","Clinical Officer","Nurse","Other"),
                                  ordered = T)]

repeated_play_data[,Level:=as.character(Level)]
repeated_play_data[,Level:=gsub('e(','e (',Level,fixed=T)]

repeated_play_data[,Level:=factor(Level,
                                  levels=c("Active Practice (Not training)","Active Practice (Training)","Student","Other"),
                                  ordered = T)]

write.csv(repeated_play_data,"repeated_play.csv",row.names = F)



e <- ggplot(repeated_play_data,aes(y=Gain,x=Time,group=SRL,color=SRL 
                                   ,linetype=SRL
                                   ))
e <- e +  scale_linetype_manual(values=c("solid","dashed","dotted","dotdash"))
e <- e + geom_smooth(size=1.025,se=FALSE) +scale_y_continuous(breaks=seq(-0.3,1,.2),limits=c(-0.3,1))
e <- e + theme_minimal(base_family="Corbel",base_size=11)
e <- e + ylab("Student Normalised Gain") + xlab("Learning Iteration")
e <- e + scale_x_continuous(breaks = scales::pretty_breaks(5), limits = c(1, NA))
e <- e + ggtitle('Learning gains from LIFE of healthcare providers\nfrom LICs by SRL profiles')
e <- e + theme(legend.position="bottom",
               #legend.direction="horizontal",
               legend.text = element_text(margin=margin(r= 10,unit="pt")),
               legend.key.width = unit(3, "line"),
               strip.text=element_text(face="bold",size=11,lineheight=5.0),
               legend.title=element_text(size=11, face="bold")
)
e <- e + guides(colour=guide_legend(override.aes=list(fill=NA)),
                linetype=guide_legend(ncol=2,byrow=F))
print(e)



f <- ggplot(repeated_play_data,aes(y=Gain,x=Time,group=SRL,color=SRL,linetype=SRL))
f <- f +  scale_linetype_manual(values=c("solid","dashed","dotted","dotdash"))
f <- f + geom_smooth(se=FALSE,lwd=1) +scale_y_continuous(breaks=seq(-0.3,1,.3),limits=c(-0.3,1))
f <- f + theme_minimal(base_family="Corbel",base_size=11)
f <- f + ylab("Student Normalised Gain") + xlab("Learning Iteration")
f <- f + facet_wrap(. ~ Level,scales='free_x',ncol=2)
f <- f + scale_x_continuous(breaks = scales::pretty_breaks(5), limits = c(1, NA))
f <- f + ggtitle('Learning gains of healthcare providers from LICs\nfrom using LIFE by SRL profiles')
f <- f + theme(legend.position="bottom",
               #legend.direction="horizontal",
               legend.text = element_text(margin=margin(r= 10,unit="pt")),
               legend.key.width = unit(1.0, "cm"),
               strip.text=element_text(face="bold",size=11,lineheight=5.0),
               legend.title=element_text(size=11, face="bold")
)
f <- f + guides(colour=guide_legend(override.aes=list(fill=NA)),
                linetype=guide_legend(ncol=2,byrow=F))
print(f)





