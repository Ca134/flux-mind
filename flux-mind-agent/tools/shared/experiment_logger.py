"""
实验日志记录模块
将实验过程中的关键事件记录为 JSONL 格式，用于后续指标计算与分析。
"""
import json
import os
from datetime import datetime


class ExperimentLogger:
    def __init__(self, log_dir="results/logs"):
        self.log_dir = log_dir
        self.session_id = None
        self.task_id = None
        self.run_id = None
        self.enabled = False  # 默认关闭，实验时手动开启

        # 会话级别的计数器
        self._counters = {}

    def enable(self):
        self.enabled = True
        os.makedirs(self.log_dir, exist_ok=True)

    def disable(self):
        self.enabled = False

    def init_session(self, session_id, task_id="unknown", run_id=0):
        self.session_id = session_id
        self.task_id = task_id
        self.run_id = run_id
        self._counters = {
            "tool_parse_success": 0,
            "tool_parse_fail": 0,
            "param_records": 0,
            "param_valid": 0,
            "param_invalid": 0,
            "rag_queries": 0,
            "optimization_count": 0,
            "preference_rerank_count": 0,
            "total_rounds": 0,
        }

    def log(self, event_type, data):
        if not self.enabled:
            return

        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": self.session_id,
            "task_id": self.task_id,
            "run_id": self.run_id,
            "event_type": event_type,
            "data": data
        }

        log_file = os.path.join(
            self.log_dir,
            f"{self.task_id}_run{self.run_id}.jsonl"
        )
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        except Exception as e:
            print(f"[ExperimentLogger] 写入日志失败: {e}")

    def increment(self, counter_name, amount=1):
        if counter_name in self._counters:
            self._counters[counter_name] += amount

    def get_counter(self, counter_name):
        return self._counters.get(counter_name, 0)

    # ---- 便捷方法 ----

    def log_tool_parse(self, success, round_number, raw_output="", parsed_tool=None,
                       parsed_params=None, error_message=None):
        if success:
            self.increment("tool_parse_success")
        else:
            self.increment("tool_parse_fail")

        self.log("tool_parse", {
            "success": success,
            "raw_output": raw_output[:500] if raw_output else "",
            "parsed_tool": parsed_tool,
            "parsed_params": parsed_params,
            "error_message": error_message,
            "round_number": round_number,
        })

    def log_param_record(self, param_name, param_value, is_valid, round_number,
                         recorded_so_far=None):
        if is_valid:
            self.increment("param_valid")
        else:
            self.increment("param_invalid")
        self.increment("param_records")

        value_type = "range" if isinstance(param_value, dict) else "exact"
        self.log("param_record", {
            "param_name": param_name,
            "param_value": param_value,
            "value_type": value_type,
            "is_valid": is_valid,
            "round_number": round_number,
            "recorded_so_far": recorded_so_far or [],
            "total_recorded": len(recorded_so_far) if recorded_so_far else 0,
        })

    def log_missing_params(self, missing_params, recorded_params, round_number):
        self.log("missing_params_query", {
            "missing_params": missing_params,
            "recorded_params": recorded_params,
            "round_number": round_number,
        })

    def log_rag_retrieval(self, query_text, results, round_number):
        self.increment("rag_queries")
        self.log("rag_retrieval", {
            "query_text": query_text,
            "top_k": len(results),
            "results": [
                {"score": r.get("score", 0), "text_preview": r.get("text", "")[:80]}
                for r in results
            ],
            "round_number": round_number,
        })

    def log_optimization_triggered(self, user_params, round_number,
                                   space_before_filter=0, space_after_filter=0):
        self.increment("optimization_count")
        self.log("optimization_triggered", {
            "user_params": user_params,
            "param_count": len(user_params),
            "round_number": round_number,
            "design_space_size_before_filter": space_before_filter,
            "design_space_size_after_filter": space_after_filter,
        })

    def log_optimization_result(self, total_candidates, pareto_count,
                                representatives, computation_time_ms=0):
        self.log("optimization_result", {
            "total_candidates": total_candidates,
            "pareto_front_size": pareto_count,
            "representatives": representatives,
            "computation_time_ms": computation_time_ms,
        })

    def log_preference_rerank(self, preference_type, strength, results):
        self.increment("preference_rerank_count")
        self.log("preference_rerank", {
            "preference_type": preference_type,
            "preference_strength": strength,
            "result_count": len(results) if isinstance(results, list) else 0,
        })

    def log_session_summary(self, final_params, optimization_triggered,
                            optimization_success):
        self.log("session_summary", {
            "total_rounds": self.get_counter("total_rounds"),
            "tool_parse_success": self.get_counter("tool_parse_success"),
            "tool_parse_fail": self.get_counter("tool_parse_fail"),
            "final_recorded_params": final_params,
            "param_completeness": f"{len(final_params)}/{len(final_params) + self.get_counter('param_invalid')}",
            "optimization_triggered": optimization_triggered,
            "optimization_success": optimization_success,
            "rag_query_count": self.get_counter("rag_queries"),
            "preference_rerank_count": self.get_counter("preference_rerank_count"),
        })


# 全局实例
exp_logger = ExperimentLogger()
