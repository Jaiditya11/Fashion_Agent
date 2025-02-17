# Fashion_Agent
## Table of Contents
1. Conceptual Map
2. Design Decisions
3. Analysis of Context Management(with example)
4. Challenges and Improvements

## Conceptual Map 🗺️
Please View the conceptual map from this link as i made it a bit big to fir here.😅
https://excalidraw.com/#json=9UrfrR9tSFpvMZbj3UCV2,JQ353h-SPx_Lj8vpCWddfA

## Design Decisions 👨🏼‍🎨
 Key Design Decisions for the **ReAct** Shopping Agent:
 
 ### ReAct Architecture Design
 
  #### Three-Component Architecture
   1.  Reasoning (Thoughts)
   2.  Acting (Tools)
   3.  Observation (Results)
  <img width="494" alt="Screenshot 2025-02-17 at 4 11 52 PM" src="https://github.com/user-attachments/assets/e07cd55f-6647-4949-811c-5822c5e5f248" />

### ShoppingTools Class contains the structure for products,promo codes & Return Policies.

<img width="306" alt="Screenshot 2025-02-17 at 4 13 47 PM" src="https://github.com/user-attachments/assets/c68eedbb-6c16-41ed-bab1-d0629936b12c" />

### The data Model for Products:

<img width="496" alt="Screenshot 2025-02-17 at 4 17 22 PM" src="https://github.com/user-attachments/assets/9fd2d811-1338-4b1a-b0a3-737e64fcdcf6" />

### Context Management

<img width="480" alt="Screenshot 2025-02-17 at 4 19 44 PM" src="https://github.com/user-attachments/assets/cce472bc-307b-457b-b71d-0363ad4613e6" />

### Information Gatering and Decision Making

<img width="576" alt="Screenshot 2025-02-17 at 4 21 31 PM" src="https://github.com/user-attachments/assets/30a5452f-e2f1-484f-ae03-400527f92fa4" />

## Analysis of Context Management(with example)

1. Basic Context Structure
   
```
#Initial Empty Context
context = {
    "query": "",               # What the user asked for
    "collected_info": {},      # Information gathered so far
    "search_criteria": {}      # What we're looking for
} 
 ```
2. Let's Follow a Real Query

 ```
 # User asks: "I need white sneakers size 8 under $70 that can arrive by Friday"

# Step 1: Context is initialized
context = {
    "query": "I need white sneakers size 8 under $70 that can arrive by Friday",
    "collected_info": {},  # Empty at start
    "search_criteria": {   # Extracted from query
        "product_type": "sneakers",
        "color": "white",
        "size": "8",
        "max_price": 70.0
    }
}

# Step 2: After product search
context["collected_info"]["search_products"] = [
    {
        "name": "White Canvas Sneakers",
        "price": 65.99,
        "size": "8",
        "color": "white",
        "store": "ShoeMart"
    }
]

# Step 3: After shipping check
context["collected_info"]["estimate_shipping"] = {
    "feasible": True,
    "cost": 12.99,
    "estimated_delivery": "2024-03-15"
}
```
3. How the context is used in decision making
   
```
def _next_thought_action(self, context: Dict):
    # 1. Check if we've searched for products
    if "search_products" not in context["collected_info"]:
        return "Need to search for products first", {
            "tool": "search_products",
            "params": context["search_criteria"]
        }
    
    # 2. If we found products and need shipping info
    if ("arrive by" in context["query"] and 
        "estimate_shipping" not in context["collected_info"]):
        
        products = context["collected_info"]["search_products"]
        return "Need to check shipping", {
            "tool": "estimate_shipping",
            "params": {
                "store": products[0]["store"],
                "target_date": "2024-03-15"
            }
        }

```
4. Example Flow

```
# Let's see how a query flows through the system:

def process_query(self, query: str):
    # 1. Initialize Context
    context = {
        "query": query,
        "collected_info": {},
        "search_criteria": self._extract_search_criteria(query)
    }
    
    # 2. First Iteration
    thought, action = self._next_thought_action(context)
    # Thought: "Need to search for products first"
    # Action: Search for white sneakers
    
    # Execute search
    search_results = self._execute_action(action)
    
    # Update context with search results
    context["collected_info"]["search_products"] = search_results
    
    # 3. Second Iteration
    thought, action = self._next_thought_action(context)
    # Thought: "Need to check shipping"
    # Action: Check shipping for found sneakers
    
    # Execute shipping check
    shipping_info = self._execute_action(action)
    
    # Update context with shipping info
    context["collected_info"]["estimate_shipping"] = shipping_info
    
    # 4. Final Response
    return self._format_final_response(context)
```
5.Visual Example of Context Evolution
```
# Starting Context
{
    "query": "white sneakers size 8 under $70 that can arrive by Friday",
    "collected_info": {},
    "search_criteria": {
        "product_type": "sneakers",
        "color": "white",
        "size": "8",
        "max_price": 70.0
    }
}

# After First Action (Product Search)
{
    "query": "white sneakers size 8 under $70 that can arrive by Friday",
    "collected_info": {
        "search_products": [
            {
                "name": "White Canvas Sneakers",
                "price": 65.99,
                "size": "8",
                "store": "ShoeMart"
            }
        ]
    },
    "search_criteria": {
        "product_type": "sneakers",
        "color": "white",
        "size": "8",
        "max_price": 70.0
    }
}

# After Second Action (Shipping Check)
{
    "query": "white sneakers size 8 under $70 that can arrive by Friday",
    "collected_info": {
        "search_products": [...],
        "estimate_shipping": {
            "feasible": True,
            "cost": 12.99,
            "estimated_delivery": "2024-03-15"
        }
    },
    "search_criteria": {...}
}
```

 
