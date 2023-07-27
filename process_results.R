# This script can eventually become an R package code

library(tidyverse)
library(lubridate)
library(rjson)

results <- fromJSON(file= 'EM_Pilot_07_26_2023_14_53_26_results.json')

experiment_info <- results[[1]]

# you can get the Python code this way, which can be used to write it to a file too
# cat(experiment_info['code'][[1]])

process_each_block <- function(i){
  results <- results[[i]]
  bind_rows(results$results) %>% 
    mutate(block = results$block,
           type = results$type,
           participant = experiment_info$participant_id,
           gender = experiment_info$participant_gender,
           age = experiment_info$participant_age,
           handedness = experiment_info$participant_handedness,
           datetime = experiment_info$datetime) %>%
    relocate(participant, gender, age, handedness, datetime, block, type)
}

# all the data from the above json file as a data frame
data_df <- 
  map_dfr(seq(2, length(results)), process_each_block) %>%
  mutate(left_larger = left_size > right_size, 
         left_press = key_pressed == 'left', 
         accuracy = left_larger == left_press) %>% 
  select(-c(left_larger, left_press, rt_time)) %>% 
  rename(rt = rt_clock)
