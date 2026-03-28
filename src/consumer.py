from confluent_kafka import Consumer
from agent_shield import SemanticShield
import json
import time

# Initialize our Redis Shield
shield = SemanticShield()

# Configure Kafka Consumer
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'agent-group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(['security-events'])

print("\n🛡️ Agent is listening to Kafka topic 'security-events'...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None: continue
        if msg.error(): continue

        payload = json.loads(msg.value().decode('utf-8'))
        prompt = payload.get("prompt", "")
        
        print(f"\n[KAFKA EVENT] Received Prompt: '{prompt}'")
        
        # 1. The Fast Path (Redis)
        is_threat, matched_pattern, latency = shield.check_threat(prompt)
        
        if is_threat:
            print(f"🛑 [BLOCKED] by Redis Semantic Firewall in {latency:.2f}ms")
            print(f"   -> Matched Known Attack: '{matched_pattern}'")
        else:
            print(f"✅ [ALLOWED] Redis cleared in {latency:.2f}ms. Forwarding to LLM Agent...")
            # Simulate slow LLM reasoning
            time.sleep(2) 
            print("   -> LLM Agent: Task executed successfully.")

except KeyboardInterrupt:
    print("Shutting down...")
finally:
    consumer.close()
