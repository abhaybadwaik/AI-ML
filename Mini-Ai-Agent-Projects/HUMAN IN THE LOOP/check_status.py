import psycopg

DB_URI = "postgresql://postgres:@127.0.0.1:5432/langgraph"

with psycopg.connect(DB_URI) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT thread_id, checkpoint FROM checkpoints ORDER BY checkpoint->>'ts' DESC")
        rows = cur.fetchall()

        seen = {}
        for row in rows:
            thread_id = row[0]
            checkpoint = row[1]
            channel_values = checkpoint.get("channel_values", {})

            if channel_values.get("amount") and thread_id not in seen:
                seen[thread_id] = {
                    "amount": channel_values.get("amount"),
                    "risk_score": channel_values.get("risk_score"),
                    "status": channel_values.get("status"),
                    "human_decision": channel_values.get("human_decision")
                }

        print("\n=== All Transactions ===\n")
        for thread_id, data in seen.items():
            if data["status"] == "completed" and data["human_decision"] is None:
                decision = "✅ AUTO APPROVED"
            elif data["human_decision"] is None:
                decision = "⏳ WAITING FOR HUMAN"
            else:
                decision = data["human_decision"]

            print(f"Thread ID  : {thread_id}")
            print(f"Amount     : ₹{data['amount']}")
            print(f"Risk Score : {data['risk_score']}")
            print(f"Status     : {data['status']}")
            print(f"Decision   : {decision}")
            print("-" * 40)