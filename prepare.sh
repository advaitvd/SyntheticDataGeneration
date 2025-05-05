#!/bin/bash

input_dir=$1
save_dir=$2

python prepare_conversation_json.py \
	--conversation_text $input_dir/conversation.text \
	--speaker_details $input_dir/speaker_details.json \
	--conversation_details $input_dir/conversation_details.json \
	--save_dir $save_dir
