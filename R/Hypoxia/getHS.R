# This file binds HS scores/labels to tiles

# Get the data for training
annot <- read.csv("/Users/chineduanene/Documents/WorkSpace/CNN_pathology/Data/RAW/Meta_file_SCC.csv")
base <- annot[c(2, 3, 4, 14)]

# Get the titles
tile <- as.data.frame(list.files("/Volumes/HDD1/Research/SCC/hypoxia/merged"))
names(tile) <- "Tile"

tile$Slide <- gsub("(.svs).*", "\\1", tile$Tile)
tile$Patient <- gsub("(-01Z).*", "\\1", tile$Tile)

tile$Patient <- as.character( lapply(tile$Patient, function(x) {
  return(substr(x, 1, nchar(x)-4))
}))

dat <- merge(tile, base, by.x = "Patient", by.y = "Case")

## Now add the class
projs <- lapply(unique(dat$Project), function(x){
  
  ds <- dat[dat$Project %in% x, ]
  
  qts <- quantile(ds$HS)
  
  ds$class <- as.numeric(Hmisc::cut2(ds$HS, g=3))
  ds$class <- ifelse(ds$class == 1, "L",
                     ifelse(ds$class == 2, "M", "H"))
  
  return(ds)
})

# Bind
projs <- do.call(rbind, projs)
plot(table(projs$Project, projs$class))
write.csv(projs, file = "labels.csv", row.names = F)

getwd()
