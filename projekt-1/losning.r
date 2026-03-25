# läser in csv datan  och sparar den i dataframen csv_data
csv_data <- read.csv2(file = 'SUSsvarNy23.csv')

# seq(1,9,2) skapar en talföljd 1,3,5,7,9, alltså udda kolumnerna
# seq(2,10,2) skapar talföljden 2,4,6,8,10, alltså jämna kolumnerna
# vi modifierar csv_datan enligt SUS reglerna för udda och jämna kolumner
csv_data[, seq(1,9,2)] <- csv_data[, seq(1,9,2)] - 1
csv_data[, seq(2,10,2)] <- 5 - csv_data[, seq(2,10,2)]

# vi summerar alla 10 värden per rad och multiplicerar med 2.5 för att normalisera till skalan 0-100
# och sparar det in i sus_score som  är en ny kolumn i dataframen csv_data
csv_data$sus_score <- rowSums(csv_data) * 2.5

# lagrar allt till variabler
sus_mean <- mean(csv_data$sus_score)
sus_median <- median(csv_data$sus_score)
sus_sd <- sd(csv_data$sus_score)
sus_min <- min(csv_data$sus_score)
sus_max <- max(csv_data$sus_score)

#vi skriver ut följande i konsolen avrundat till 2 decimaler
sprintf("medelvärde: %.2f", sus_mean)
sprintf("median: %.2f", sus_median)
sprintf("standardavvikelse: %.2f", sus_sd)
sprintf("minimum: %.2f", sus_min)
sprintf("maximum: %.2f", sus_max)