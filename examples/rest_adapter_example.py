#!/usr/bin/env python3
"""
Example demonstrating the RESTAdapter with JSONPlaceholder API.

This example shows how to:
1. Create a RESTAdapter for the JSONPlaceholder API
2. Query different endpoints (users, posts, comments)
3. Use the Router to manage multiple data sources
4. Perform various queries and data operations
"""

import pandas as pd

from data_agents.adapters import RESTAdapter, TabularAdapter
from data_agents.core import Router


def main() -> None:
    """Demonstrate RESTAdapter functionality with JSONPlaceholder."""
    print("🌐 REST Adapter Example with JSONPlaceholder API")
    print("=" * 50)

    # Create a RESTAdapter for JSONPlaceholder
    jsonplaceholder_config = {
        "headers": {"User-Agent": "DataAgents-Example/1.0"},
        "timeout": 10,
        # JSONPlaceholder endpoints for discovery
        "endpoints": ["users", "posts", "comments", "albums", "photos", "todos"],
        "pagination_param": "_limit",  # JSONPlaceholder uses _limit for pagination
        "pagination_limit": 3,
    }

    api_adapter = RESTAdapter(
        name="jsonplaceholder",
        base_url="https://jsonplaceholder.typicode.com",
        config=jsonplaceholder_config,
    )

    print("\n1. 📋 Getting API Discovery Information")
    print("-" * 35)
    discovery = api_adapter.discover()
    print(f"Base URL: {discovery['base_url']}")
    print(f"Available endpoints: {discovery['available_endpoints']}")
    print(f"Schema endpoints: {list(discovery['endpoints'].keys())}")
    print(f"Sample data available for: {list(discovery['sample_data'].keys())}")

    print("\n2. 👥 Querying Users")
    print("-" * 20)
    users_df = api_adapter.query("users")
    print(f"Found {len(users_df)} users")
    print("Sample user data:")
    print(users_df[["id", "name", "email", "website"]].head(3))

    print("\n3. 📝 Querying Posts")
    print("-" * 20)
    posts_df = api_adapter.query("posts", params={"_limit": 5})
    print(f"Found {len(posts_df)} posts (limited to 5)")
    print("Sample post data:")
    print(posts_df[["id", "userId", "title"]].head())

    print("\n4. 💬 Querying Comments for a Specific Post")
    print("-" * 40)
    comments_df = api_adapter.query("posts/1/comments")
    print(f"Found {len(comments_df)} comments for post 1")
    print("Sample comment data:")
    print(comments_df[["id", "name", "email"]].head(3))

    print("\n5. 🔍 Single User Query")
    print("-" * 25)
    user_df = api_adapter.query("users/1")
    print("User 1 details:")
    print(user_df[["name", "email", "phone", "website"]])

    print("\n6. 🏢 Creating a Router with Multiple Adapters")
    print("-" * 45)

    # Create a router and add both REST and tabular adapters
    router = Router("demo_router")
    router.register_adapter(api_adapter)

    # Create some sample local data
    local_data = pd.DataFrame(
        {
            "user_id": [1, 2, 3, 4, 5],
            "local_score": [85, 92, 78, 96, 88],
            "category": ["A", "B", "A", "A", "B"],
            "last_updated": pd.to_datetime(
                ["2024-01-15", "2024-01-16", "2024-01-17", "2024-01-18", "2024-01-19"]
            ),
        }
    )

    local_adapter = TabularAdapter("local_scores", local_data)
    router.register_adapter(local_adapter)

    print(f"Router has {len(router.list_adapters())} adapters:")
    for adapter_name in router.list_adapters():
        print(f"  - {adapter_name}")

    print("\n7. 📊 Combining Data from Multiple Sources")
    print("-" * 42)

    # Get users from API
    api_users = router.query("jsonplaceholder", "users")
    print(f"API users: {len(api_users)} records")

    # Get local scores
    local_scores = router.query("local_scores", "*")
    print(f"Local scores: {len(local_scores)} records")

    # Simple join demonstration (if user IDs match)
    if not api_users.empty and not local_scores.empty:
        # Merge on user_id (assuming API id matches local user_id)
        merged_df = pd.merge(
            api_users[["id", "name", "email"]],
            local_scores,
            left_on="id",
            right_on="user_id",
            how="inner",
        )

        if not merged_df.empty:
            print("\n🔗 Merged data (API users + local scores):")
            print(merged_df[["name", "email", "local_score", "category"]])
        else:
            print("No matching user IDs found for merge")

    print("\n8. 🛠️ Testing Different HTTP Methods")
    print("-" * 38)

    # Test POST (JSONPlaceholder accepts POST requests and returns mock responses)
    try:
        new_post_data = {
            "title": "Test Post from DataAgents",
            "body": "This is a test post created using the RESTAdapter",
            "userId": 1,
        }

        post_response = api_adapter.post_data("posts", new_post_data)
        print("✅ POST request successful:")
        print(f"Created post with ID: {post_response['id'].iloc[0]}")
        print(f"Title: {post_response['title'].iloc[0]}")

    except Exception as e:
        print(f"❌ POST request failed: {e}")

    print("\n9. 📈 Router Information")
    print("-" * 25)
    router_info = router.get_info()
    print(f"Router: {router_info['name']}")
    print(f"Adapter count: {router_info['adapter_count']}")
    print("Adapter details:")
    for name, info in router_info["adapters"].items():
        print(f"  - {name}: {info['type']}")

    print("\n✨ Example completed successfully!")
    print("The RESTAdapter provides a powerful way to integrate REST APIs")
    print("into your data processing workflows alongside other data sources.")


if __name__ == "__main__":
    main()
