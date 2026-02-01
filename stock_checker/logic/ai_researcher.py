import os
import re
from google import genai
from google.genai import types

class AIResearcher:
    def __init__(self, api_key):
        self.api_key = api_key
        try:
            self.client = genai.Client(api_key=self.api_key)
            # Default model to try
            self.model_name = "gemini-3-pro-preview" 
        except Exception as e:
            print(f"Error configuring Gemini: {e}")
            self.client = None

    def analyze_with_gemini(self, prompt_path="prompt.txt", selected_model=None):
        """
        Loads prompt from file and executes with Google Search Grounding using google-genai SDK.
        """
        if not self.client:
            return {"error": "API Key not configured."}

        # 1. Load Prompt
        # Fix: Resolve path relative to this file if default path is used and file not found in CWD
        if prompt_path == "prompt.txt" and not os.path.exists(prompt_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            prompt_path = os.path.join(base_dir, "prompt.txt")

        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_content = f.read()
        except FileNotFoundError:
            return {"error": f"プロンプトファイル {prompt_path} が見つかりませんでした。"}
        except Exception as e:
            return {"error": f"プロンプト読み込みエラー: {e}"}

        # 2. Generate Content with Search Tool (Grounding)
        try:
            # Code adaptation from user snippet
            search_tool = types.Tool(
                google_search=types.GoogleSearch()
            )

            # Try preferred models
            # If a model is selected in UI, try it first.
            candidates = []
            if selected_model:
                candidates.append(selected_model)
            
            candidates.extend([
                'gemini-3-pro-preview', 
                'gemini-2.5-flash', 
                'gemini-2.0-pro-exp-02-05',
                'gemini-1.5-pro',
                'gemini-1.5-flash',
                'gemini-2.0-flash-001'
            ])
            
            # Deduplicate while preserving order
            unique_candidates = []
            for c in candidates:
                if c not in unique_candidates:
                    unique_candidates.append(c)
            
            response = None
            errors = []

            for model in unique_candidates:
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt_content,
                        config=types.GenerateContentConfig(
                            tools=[search_tool],
                            temperature=1.0 # Recommended for grounding
                        )
                    )
                    self.model_name = model
                    break
                except Exception as e:
                    errors.append(f"{model}: {str(e)}")
                    continue
            
            if not response:
                error_details = "\n".join(errors)
                return {"error": f"全てのモデルで生成に失敗しました。\n詳細:\n{error_details}"}

            text = response.text
            return self._parse_response(text)
            
        except Exception as e:
            error_msg = str(e)
            return {"error": f"AI生成エラー (Grounding/NewSDK): {error_msg}"}
            
            text = response.text
            return self._parse_response(text)
            
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                 return {"error": f"モデルが見つかりません。APIキーまたはモデル名を確認してください。\nDetails: {error_msg}"}
            
            # Fallback: Try without explicit tool arg keywords if syntax was wrong, 
            # trusting the prompt instructions if the model has default access (unlikely but possible for some keys)
            # Or return error.
            return {"error": f"AI生成エラー (Grounding): {error_msg}"}

    def _parse_response(self, text):
        """
        Parses the text response to extract structured stock data.
        Expected format: "### ■ 銘柄：Company (1234) 【Short/Medium】"
        """
        parsed_items = []
        
        # Split by the header pattern "### ■"
        # This gives us chunks starting with " 銘柄：..."
        chunks = re.split(r'### ■', text)
        
        for chunk in chunks:
            if not chunk.strip():
                continue
                
            # Regex to extract Name, Ticker, Strategy
            # Pattern: 銘柄：(Name)（(Ticker)）(Something about Strategy)
            # Ticker: 4 digits
            # Strategy: 【...】 or just text
            
            # Helper to find ticker (most critical)
            ticker_match = re.search(r'[（\(](\d{4})[）\)]', chunk)
            if ticker_match:
                ticker = ticker_match.group(1)
                
                # Extract Name (Before the ticker)
                # chunk starts with " 銘柄：Name（..."
                # Clean up " 銘柄：" prefix
                lines = chunk.strip().split('\n')
                header_line = lines[0]
                
                # Remove "銘柄："
                clean_header = header_line.replace("銘柄：", "").strip()
                
                # Extract Strategy if present in 【】
                strategy = "不明"
                if "【短期】" in clean_header:
                    strategy = "短期"
                elif "【中期】" in clean_header:
                    strategy = "中期"
                
                # Extract Name: everything before the ticker parenthesis
                # e.g. "Toyota (7203) 【Medium】" -> "Toyota " causes split
                # Let's just split by the ticker part
                name_part = re.split(r'[（\(]\d{4}[）\)]', clean_header)[0].strip()
                
                parsed_items.append({
                    "ticker": ticker,
                    "name": name_part,
                    "strategy": strategy,
                    "full_text": "### ■" + chunk # Reconstruct for display context if needed
                })
                
        # Deduplicate by ticker (keep first found?? or list all?)
        # User wants 3 short + 3 medium. Duplicates unlikely but good to handle.
        unique_items = []
        seen_tickers = set()
        for item in parsed_items:
            if item['ticker'] not in seen_tickers:
                seen_tickers.add(item['ticker'])
                unique_items.append(item)

        return {
            "full_report": text,
            "items": unique_items # structured list
        }

