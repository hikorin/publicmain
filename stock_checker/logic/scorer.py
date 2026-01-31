class Scorer:
    def __init__(self, stock_data):
        self.stock = stock_data
        self.results = {}

    def evaluate_short_term(self):
        beta = self.stock.calculate_beta()
        rsi = self.stock.calculate_rsi()
        volume_surge = self.stock.check_volume_surge()

        score = 0
        details = []

        # Beta > 1.2
        if beta is not None:
            if beta > 1.2:
                score += 40
                details.append(f"高ベータ: {beta:.2f} (順張りトレンド)")
            else:
                details.append(f"ベータ: {beta:.2f}")
        else:
             details.append("ベータ: データなし")

        # RSI logic
        if rsi is not None:
            if rsi <= 30:
                score += 30
                details.append(f"RSI 売られすぎ: {rsi:.2f}")
            elif rsi >= 80:
                details.append(f"RSI 買われすぎ: {rsi:.2f}")
            else:
                details.append(f"RSI 中立: {rsi:.2f}")
        else:
             details.append("RSI: データなし")

        # Volume Surge
        if volume_surge:
            score += 30
            details.append("出来高急増を検知")

        return {
            "score": min(score, 100),
            "beta": beta,
            "rsi": rsi,
            "volume_surge": volume_surge,
            "details": details
        }

    def evaluate_medium_term(self):
        funds = self.stock.get_fundamentals()
        equity_ratio = self.stock.calculate_equity_ratio()
        
        roe = funds.get("roe")
        per = funds.get("per")
        growth = funds.get("revenue_growth")

        score = 0
        details = []

        # ROE >= 10% (0.10)
        if roe is not None:
            if roe >= 0.10:
                score += 25
                details.append(f"高ROE: {roe:.1%}")
            else:
                 details.append(f"ROE: {roe:.1%}")
        else:
            details.append("ROE: データなし")

        # PER <= 15
        if per is not None:
            if per <= 15:
                score += 25
                details.append(f"割安PER: {per:.2f}")
            else:
                details.append(f"PER: {per:.2f}")
        else:
            details.append("PER: データなし")

        # Equity Ratio >= 40%
        if equity_ratio is not None:
            if equity_ratio >= 0.40:
                score += 25
                details.append(f"高安全性 (自己資本比率): {equity_ratio:.1%}")
            else:
                details.append(f"自己資本比率: {equity_ratio:.1%}")
        else:
            details.append("自己資本比率: データなし")

        # Revenue Growth >= 5%
        if growth is not None:
            if growth >= 0.05:
                score += 25
                details.append(f"高成長 (売上): {growth:.1%}")
            else:
                details.append(f"売上成長率: {growth:.1%}")
        else:
            details.append("売上成長率: データなし")

        return {
            "score": min(score, 100),
            "roe": roe,
            "per": per,
            "equity_ratio": equity_ratio,
            "revenue_growth": growth,
            "details": details
        }
