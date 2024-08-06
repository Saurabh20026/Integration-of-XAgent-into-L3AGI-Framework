def test_error_handling():
    config = XAgentConfig()
    agent = XAgent(config)
    
    # Test with an invalid query
    try:
        result = agent.run("@#$%^&*")
        print(f"Invalid query result: {result}")
    except Exception as e:
        print(f"Handled error for invalid query: {str(e)}")

    # Test with a very long input
    long_input = "a" * 10000
    try:
        result = agent.run(long_input)
        print(f"Long input result: {result[:100]}...")
    except Exception as e:
        print(f"Handled error for long input: {str(e)}")

if __name__ == '__main__':
    test_error_handling()