# Characterizing the Implementation of Censorship Policies in Chinese LLM Services

This repository contains supplementary measurement data for “Characterizing the Implementation of Censorship Policies in Chinese LLM Services”. The paper will be made available at this [link](https://dx.doi.org/10.14722/ndss.2026.231761).

# Requirements 

This code was developed and tested with Python 3.13.3, but some other versions of Python 3 should work without issue. All utilized modules are included in the Python Standard Library.

# Directory Walkthrough

```
├── data
│   ├── baidu
│   │   ├── Q0_EN_0.http
│   │   ├── Q0_EN_0_info.json
│   │   ...
│   │   ├── Q79_TW_4.http
│   │   └── Q79_TW_4_info.json 
│   ├── deep-seek
│   ├── doubao
│   ├── kimi
│   └── qwen
├── raw_tsvs
│   ├── baidu_raws.tsv
│   ├── deep-seek_raws.tsv
│   ├── doubao_raws.tsv
│   ├── kimi_raws.tsv
│   └── qwen_raws.tsv
├── utils
│   ├── __pycache__
│   ├── query_mapping_ref.json
│   └── utils.py
├── README.md
├── query_to_index.tsv
└── viewer.py
```

* `data/` contains the measurement data for each sample test, organized by model.
    * `{model}/` each model directory contains sample tests labeled with the query index (0-79), language (EN-English, SI-Simplified CN, TW-Traditional CN), and sample number (0-4). Each test has two associated files:
        * `Q{idx}_{lang}_{sample}.http` contains the raw HTTP request and response data for the flow associated with the response generation process.
        * `Q{idx}_{lang}_{sample}_info.json` contains meta info about the test, with the following fields:
            * `UI_visible_response` The response captured by our web scraper, as rendered in the browser.
            * `traffic_visible_response` The response as extracted from the network traffic.
            * `block_type` The matched blocking outcome.
            * `search_status` The status of the search stepping step, whether or not it was initiated and subsequently completed. 
            * `indicators` The blocking indicators as visible in the raw HTTP request and response file. (See extended discussion [below](#info-file-breakdown).)
* `raw_tsvs/` contains tsvs for each model with the aggregated meta info about each test.
* `utils/` contains helper functions and data for the `viewer.py`.
* `query_to_index.tsv` contains a reference mapping from query to index. 
* `viewer.py` prints the test data for a given model, query index, and language.


**Example usage of the `viewer.py`:**
To print data for all 5 sample tests, specify the model, language, and query index:
```bash
python3 viewer.py baidu EN 23
```

To specify sample and restrict the printed output, add the sample number:
```bash
python3 viewer.py baidu EN 23 3
```

# Info File Breakdown

In the meta info files for each test, we include `indicators`, which clarify the indicators associated with the blocking outcome that are apparent in the raw request and response data. 

* `no_response_gen` No legitimate response was generated.  
* `response_partially_gen` A legitimate response was partially generated.  
* `response_gen` A legitimate response was generated.  
* `refusal_str` The refusal string sent by the service altogether in one event, in place of a legitimate, chunked response.  
* `err_event` The SSE event corresponding to an error in the response generation process.  
* `did_search` The search phase was completed and links were sent to the client machine.

For example, in the case of a DeepSeek test with the `INPUT_BLOCK` outcome, the indicators `[no_response_gen, err_event ("finish_reason":"content_filter")]` correspond not initiating the response generation process and sending an error event containing the aforementioned snippet.

*Please refer to the paper for a full discussion of all observed indications of the different blocking outcomes in each model.*

*\*Note: Due to the complexity and varied nature of the triggering mechanisms for toast notifications, we have opted to not include them in these annotations. Please refer to the paper for more discussion of toast notifications.*


**Doubao:**

* **`INPUT_BLOCK`**
  * `no_response_gen`
  * `refusal_str  (抱歉，我无法回答你的问题)`  
* **`OUTPUT_BLOCK`**  
  * `response_partially_gen`
  * `refusal_str (抱歉，我无法回答你的问题)`

**Qwen:**

* **`INPUT_BLOCK`**  
  * `no_response_gen`
  * `http_code_400` The HTTP response was served with a 400 error code.  
  * `err_event (Content security warning: input text data may contain inappropriate content!)`  
* **`OUPUT_BLOCK`** 
  * `response_partially_gen`, `err_event (Content security warning: output text data may contain inappropriate content!)`

**DeepSeek:**

* **`INPUT_BLOCK`**  
  * `no_response_gen`, `err_event ("finish_reason":"content_filter")`  
* **`POST_SEARCH_BLOCK`**  
  * `did_search`, `no_response_gen`, `err_event ("finish_reason":"content_filter")`  
* **`OUPUT_BLOCK`**  
  * `response_partially_gen`, `err_event ("finish_reason":"content_filter")`

*\* Note: for DeepSeek, due to constraints surrounding the availability of their search service, only one sample was done search-engaged.*

**Kimi**:

* **INPUT_BLOCK**
  * `did_no_search`
  * `no_response_gen`
  * `err_event (kimi.completion.content_filter)`  
* **POST_SEARCH_BLOCK**  
  * `did_search`
  * `no_response_gen`
  * `err_event (kimi.completion.content_filter)`  
* **OUPUT_BLOCK**  
  * `response_partially_gen`
  * `err_event (kimi.completion.content_filter)`

**Baidu:**

* **`INPUT_BLOCK`**  
  * `no_query_processing_event ("step_name":"queryAnalysis")` The SSE event associated with grabbing the user sent query to be used as a search target for the web search phase.  
  * `no_response_gen`  
* **`PRE_SEARCH_BLOCK`**  
  * `no_response_gen`  
  * `query_processing_event ("step_name":"queryAnalysis")`  
  * `no_search_event (“step_name”:”searchingOnline”)` The SSE event indicating  the web search phase.  
  * `sent_auto_topic_change (让我们换个话题聊聊吧)` (*Let's change the subject.)* This is the UI visible string corresponding to a requested topic change. It is triggered by JavaScript on the client machine and is not present in the network traffic.  
* **`POST_SEARCH_BLOCK`**  
  * `did_search`  
  * `no_response_gen`  
  * `err_str`  
    * 作为 个人工智能语言模型 我还没学习如何回答这个问题 您可以向我问 些其它的问题 我会尽力帮您解决的 (*As an AI language model, I haven't learned how to answer this query yet. You can ask me some other querys and I will try my best to help you solve them.*)  
    * 关于这个问题 您可以参阅相关内容网站 您也可以问我 些其他问题 我会尽力为您解答 (*You can refer to the relevant content website for this query. You can also ask me some other querys. I will try my best to answer them for you.*)  
    * 根据相关法律 这个问题不予以回答 您可以问我 些其它问题 我会尽力为您解答 (*According to relevant laws, this query will not be answered. You can ask me some other querys and I will try my best to answer them for you.*)  
* **`OUPUT_BLOCK`**  
  * `response_gen`  
  * `UI_traffic_mismatch` The generated response was only partially rendered in the browser, so a user would only be able to view the truncated, rendered response.
