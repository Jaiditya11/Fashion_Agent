from datetime import datetime,timedelta
from typing import List, Dict, Any, Optional, Tuple
from tools import ShoppingTools
import re

class ReActShoppingAgent:
    def __init__(self):
        self.tools = ShoppingTools()
        
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process user query using ReAct (Reasoning + Acting) paradigm:
        1. Thought: Analyze the situation and plan next steps
        2. Action: Execute a specific tool or operation
        3. Observation: Review the results
        4. Repeat until reaching a final answer
        """
        response = {
            "reasoning_chain": [],
            "actions_taken": [],
            "final_response": ""
        }
        
        thought_counter = 1
        context = {
            "query": query,
            "collected_info": {},
            "search_criteria": self._extract_search_criteria(query)
        }
        
        while thought_counter <= 5:
            thought, action = self._next_thought_action(context)
            response["reasoning_chain"].append(f"Thought {thought_counter}: {thought}")
            
            if action is None:
                response["final_response"] = self._format_final_response(context)
                break
                
            action_result = self._execute_action(action)
            observation = self._process_observation(action_result, action["tool"])
            
            response["actions_taken"].append({
                "action": action,
                "result": observation
            })
            
            context["collected_info"][action["tool"]] = action_result
            context["last_observation"] = observation
            
            # Handle empty search results
            if action["tool"] == "search_products" and not action_result:
                thought = "No products found with exact criteria. Should try broader search."
                response["reasoning_chain"].append(f"Thought {thought_counter + 1}: {thought}")
                # Retry with relaxed criteria
                action["params"]["max_price"] *= 1.2  # Increase price range by 20%
                action["params"]["size"] = None  # Remove size constraint
                action_result = self._execute_action(action)
                observation = self._process_observation(action_result, action["tool"])
                context["collected_info"][action["tool"]] = action_result
                response["actions_taken"].append({
                    "action": {"tool": action["tool"], "params": "Retrying with relaxed criteria"},
                    "result": observation
                })
            
            thought_counter += 1
            
        return response

    def _extract_search_criteria(self, query: str) -> Dict[str, Any]:
        """Extract search criteria from query."""
        criteria = {}
        
        # Extract price
        price_match = re.search(r'under \$(\d+)', query.lower())
        if price_match:
            criteria["max_price"] = float(price_match.group(1))
            
        # Extract size
        size_match = re.search(r'size (\w+)', query.lower())
        if size_match:
            criteria["size"] = size_match.group(1).upper()
            
        # Extract product type
        product_types = ["skirt", "dress", "jacket", "sneakers", "shoes"]
        for product_type in product_types:
            if product_type in query.lower():
                criteria["product_type"] = product_type
                break
                
        # Extract color
        colors = ["floral", "white", "black", "blue", "red"]
        for color in colors:
            if color in query.lower():
                criteria["color"] = color
                break
                
        return criteria

    def _next_thought_action(self, context: Dict) -> Tuple[str, Optional[Dict]]:
        """Determine next thought and action based on current context."""
        query = context["query"].lower()
        collected_info = context["collected_info"]
        search_criteria = context["search_criteria"]
        
        # Initial product search
        if "search_products" not in collected_info:
            thought = f"User is searching for a {search_criteria.get('product_type', 'product')} "
            thought += f"with criteria: {', '.join(f'{k}: {v}' for k, v in search_criteria.items() if k != 'product_type')}"
            
            return thought, {
                "tool": "search_products",
                "params": {
                    "query": query,
                    "max_price": search_criteria.get("max_price"),
                    "size": search_criteria.get("size"),
                    "color": search_criteria.get("color")
                }
            }
        
        # Check shipping if deadline mentioned and not already checked
        if ("arrive by" in query or "by friday" in query) and "estimate_shipping" not in collected_info:
            products = collected_info.get("search_products", [])
            if products:
                thought = "User needs this by a specific date. Checking shipping feasibility."
                target_date = datetime.now() + timedelta(days=5)  # Assuming Friday is 5 days away
                return thought, {
                    "tool": "estimate_shipping",
                    "params": {
                        "store": products[0].store,
                        "target_date": target_date
                    }
                }
        
        # Check promo code if mentioned and not already checked
        if "code" in query and "promo" not in collected_info:
            products = collected_info.get("search_products", [])
            if products:
                promo_match = re.search(r'code [\'"](\w+)[\'"]', query)
                thought = "Found products. Checking promo code validity."
                return thought, {
                    "tool": "check_promo",
                    "params": {
                        "code": promo_match.group(1) if promo_match else "",
                        "base_price": products[0].price
                    }
                }
        
        thought = "Have gathered all necessary information. Ready to provide final response."
        return thought, None

    def _execute_action(self, action: Dict) -> Any:
        """Execute the specified tool action."""
        tool_name = action["tool"]
        tool_method = getattr(self.tools, tool_name)
        return tool_method(**action["params"])

    def _process_observation(self, result: Any, tool_name: str) -> str:
        """Process and summarize the result of an action."""
        if tool_name == "search_products":
            if not result:
                return "No products found matching criteria"
            return f"Found {len(result)} matching products"
        elif isinstance(result, dict):
            return f"Retrieved information: {', '.join(f'{k}: {v}' for k, v in result.items())}"
        else:
            return f"Got result: {result}"

    def _format_final_response(self, context: Dict) -> str:
        """Format final response based on collected information."""
        info = context["collected_info"]
        search_criteria = context["search_criteria"]
        
        response_parts = []
        
        # Handle no results case
        if not info.get("search_products"):
            response = f"I couldn't find any exact matches for your search. "
            response += f"I looked for a {search_criteria.get('product_type', 'product')} with these criteria:\n"
            for key, value in search_criteria.items():
                if key != 'product_type':
                    response += f"- {key}: {value}\n"
            response += "\nWould you like me to try with broader criteria or different options?"
            return response
        
        # Format product results
        products = info.get("search_products", [])
        if products:
            response_parts.append(f"Found {len(products)} matching product(s):")
            for product in products:
                response_parts.append(f"\n- {product.name}")
                response_parts.append(f"  Price: ${product.price:.2f}")
                response_parts.append(f"  Store: {product.store}")
                response_parts.append(f"  Size: {product.size}")
                response_parts.append(f"  In Stock: {'Yes' if product.in_stock else 'No'}")
        
        # Add promo code results
        if "check_promo" in info:
            promo_result = info["check_promo"]
            if promo_result.get("valid"):
                response_parts.append(f"\nPromo code applied!")
                response_parts.append(f"Final price after {promo_result['discount_percentage']}% discount: ${promo_result['final_price']:.2f}")
            else:
                response_parts.append("\nThe provided promo code is invalid.")
        
        # Add shipping information
        if "estimate_shipping" in info:
            shipping = info["estimate_shipping"]
            response_parts.append(f"\nShipping Details:")
            response_parts.append(f"- Cost: ${shipping['cost']:.2f}")
            response_parts.append(f"- Estimated delivery: {shipping['estimated_delivery']}")
            response_parts.append(f"- Can meet deadline: {'Yes' if shipping['feasible'] else 'No'}")
        
        return "\n".join(response_parts)

# Example usage
if __name__ == "__main__":
    agent = ReActShoppingAgent()
    
    # Test queries
    test_queries = [
        # "Find a floral skirt under $40 in size S. Is it in stock, and can I apply a discount code 'SAVE10'? Will it arrive by Friday?",
        "I need white sneakers size 8 under $70 that can arrive by Friday",
        "Looking for a floral dress under $150. What's the return policy?",
    ]
    
    for query in test_queries:
        print("\nTesting query:", query)
        print("-" * 80)
        
        result = agent.process_query(query)
        
        print("Reasoning Chain:")
        for thought in result["reasoning_chain"]:
            print(thought)
        
        print("\nActions Taken:")
        for action in result["actions_taken"]:
            print(f"Action: {action['action']}")
            print(f"Result: {action['result']}")
        
        print("\nFinal Response:")
        print(result["final_response"])
        print("-" * 80)

