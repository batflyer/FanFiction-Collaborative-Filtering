#!/usr/bin/env bash

#   Copyright (c) 2018 Alexander L. Hayes (@batflyer)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

BASE="https://www.fanfiction.net/book/Hitchhiker-s-Guide-to-the-Galaxy/?&srt=1&r=10&p="

for i in {1..25}; do
  URL=$BASE$i
  echo "$URL"
  PAGE="`wget --no-check-certificate -q -O - $URL`"
  echo "$PAGE" | grep "class=stitle" | cut -c117-137 | cut -d'/' -f 3 >> data/Hitchhikers/sids.txt
  sleep 3
done
