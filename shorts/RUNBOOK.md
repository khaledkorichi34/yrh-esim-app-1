# YRH eSIM daily Short — runbook

One vertical Short per day on YouTube channel **@yrhesim**, rotating 14 countries
(`countries.json`). Each video speaks the country's language to its residents who travel abroad,
with real prices from yrh.ai. Gemini writes, Fable reviews, Gemini voices, Claude renders and publishes.
The video goes up as *private + scheduled* for 18:30 local time in the target country.

Everything lives on branch `youtube-assets` of `khaledkorichi34/yrh-esim-app-1`.

## Make scenarios (team 1232334)
| what | scenario | tool |
|---|---|---|
| yrh.ai WooCommerce API | 10079107 | `s10079107_wp_yrhai_api_auth` (method, path) |
| Gemini text | 9956278 | `s9956278_gemini_ask_text_prompt` (prompt, system, model) |
| Fable (OpenRouter) | 10078512 | `s10078512_open_router_ask_fable` (prompt, system, max_tokens) |
| Gemini TTS -> repo | 10111683 | `scenarios_run` with data {text, voice, path} (responsive) |
| Gemini Lyria music -> repo | 10111688 | `scenarios_run` with data {prompt, path} |
| YouTube upload (@yrhesim) | 10111677 | `scenarios_run` with data {video_url, title, description, tags, publish_at} |

Long Gemini/Fable runs may return only an executionId: read the result with `executions_get-detail`
(scenarioId + executionId) until status is SUCCESS.

## Daily steps
Work in a clone of the branch: `git clone --depth 1 -b youtube-assets https://github.com/khaledkorichi34/yrh-esim-app-1 yrh && cd yrh/shorts`
(if the repo is not reachable, attach it first with `add_repo` owner `khaledkorichi34`, repo `yrh-esim-app-1`, access `push`).

1. `python3 prepare.py next` — prints JOB id, publish time and 3 product slugs.
2. For each slug: `GET /wp-json/wc/v3/products?slug=<slug>&_fields=id` then
   `GET /wp-json/wc/v3/products/<id>/variations?per_page=50&_fields=price,attributes`.
   Save the tool output to a file and run `python3 prepare.py prices <JOB> <key> <file>`.
   If a product is missing or out of stock, swap that key in `jobs/<JOB>/plan.json` for `global` and continue.
3. `python3 prepare.py prompt <JOB>` -> send to Gemini (model `gemini-pro-latest`, system:
   "You are a top direct-response copywriter for travel-tech Shorts. You write native, natural copy. Output ONLY valid JSON.").
   Save the answer as `jobs/<JOB>/script_gemini.json`.
4. `python3 prepare.py review <JOB> jobs/<JOB>/script_gemini.json` -> send to Fable (max_tokens 4000, system:
   "You are a strict ad reviewer and native copy editor. Output ONLY the corrected JSON."). Save as `jobs/<JOB>/script.json`.
5. `python3 prepare.py spec <JOB> jobs/<JOB>/script.json` — validates prices, writes spec/meta, prints the TTS text.
   If it rejects a price, fix that line yourself using only the allowed prices, then rerun.
6. Voice: run scenario 10111683 with {text: contents of `jobs/<JOB>/tts.txt`, voice: meta.voice, path: `audio/<JOB>.wav`}; then `git pull`.
7. Render: `python3 render.py jobs/<JOB>/spec.json ../audio/<JOB>.wav ../<meta.music> ../videos/<JOB>.mp4`
   (the voice must split into 5 parts; check the printed scene durations are each 2.5–10 s).
8. QA: extract frames at 1.5 s, middle of each scene and 1 s before the end (`ffmpeg -ss T -i video -frames:v 1`),
   look at them: text readable, not clipped, correct script direction, prices match the card list. Fix and re-render if not.
9. Publish: commit `videos/<JOB>.mp4`, `jobs/<JOB>/`, push to `youtube-assets`, then run scenario 10111677 with
   video_url `https://raw.githubusercontent.com/khaledkorichi34/yrh-esim-app-1/youtube-assets/videos/<JOB>.mp4`,
   title, description, tags from `meta.json`, and publish_at from `meta.json`.
10. `python3 prepare.py done <JOB> <videoId>`, commit state.json and push.
11. Report in Arabic to Khaled (SendUserMessage): country, destinations, title, the scheduled time, link `https://youtu.be/<videoId>`.

Never publish a price that is not in that day's yrh.ai data. If any step fails twice, stop and report what failed.
