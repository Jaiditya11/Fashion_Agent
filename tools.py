

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
import random

class Product:
    def __init__(self, name: str, price: float, size: str, color: str, store: str):
        self.name = name
        self.price = price
        self.size = size
        self.color = color
        self.store = store
        self.in_stock = random.choice([True, False])

class ShoppingTools:
    def __init__(self):
        # mock product database 
        self.products = [
            Product("Floral A-Line Skirt", 35.99, "S", "floral", "FashionStore"),
            Product("Floral Pleated Skirt", 42.99, "S", "floral", "StyleHub"),
            Product("White Canvas Sneakers", 65.99, "8", "white", "ShoeMart"),
            Product("White Running Shoes", 69.99, "8", "white", "SportStyle"),
            Product("Classic Denim Jacket", 79.99, "M", "blue", "DenimCo"),
            Product("Vintage Denim Jacket", 72.99, "M", "blue", "VintageStyle"),
            Product("Black Cocktail Dress", 129.99, "M", "black", "EveningWear"),
            Product("Floral Summer Skirt", 38.99, "S", "floral", "StyleHub"),
            Product("White Fashion Sneakers", 68.99, "8", "white", "FashionFeet"),
            Product("Black Evening Dress", 145.99, "S", "black", "ElegantWear")
        ]
        
        self.promo_codes = {
            "SAVE10": 0.10,
            "SPRING20": 0.20,
            "SUMMER15": 0.15
        }
        
        self.return_policies = {
            "FashionStore": "30-day returns with original tags. Free returns.",
            "StyleHub": "14-day returns. Customer pays return shipping.",
            "ShoeMart": "60-day returns. Free returns with membership.",
            "DenimCo": "45-day returns. Free in-store returns.",
            "EveningWear": "7-day returns for unworn items only.",
            "FashionFeet": "30-day returns, free shipping.",
            "ElegantWear": "21-day returns for unworn items."
        }

    def search_products(self, 
                       query: str, 
                       max_price: Optional[float] = None,
                       size: Optional[str] = None,
                       color: Optional[str] = None) -> List[Product]:
        """Enhanced search for products matching the given criteria."""
        results = []
        
        # Extract keywords from query
        query_words = set(query.lower().split())
        
        for product in self.products:
            # Initialize match score
            matches = True
            
            # Check price constraint
            if max_price and product.price > max_price:
                matches = False
                continue
                
            # Check size if specified
            if size and size.upper() != product.size.upper():
                matches = False
                continue
                
            # Check color if specified
            if color and color.lower() not in product.color.lower():
                matches = False
                continue
            
            # If all criteria match, add to results
            if matches:
                results.append(product)
                
        return results

    def estimate_shipping(self, 
                         store: str, 
                         target_date: datetime) -> Dict[str, Union[bool, float, str]]:
        """Estimate shipping time and cost."""
        days_to_deliver = random.randint(2, 7)
        estimated_delivery = datetime.now() + timedelta(days=days_to_deliver)
        shipping_cost = random.uniform(5.99, 15.99)
        
        return {
            "feasible": estimated_delivery <= target_date,
            "cost": round(shipping_cost, 2),
            "estimated_delivery": estimated_delivery.strftime("%Y-%m-%d"),
            "store": store
        }

    def check_promo(self, code: str, base_price: float) -> Dict[str, Union[bool, float, str]]:
        """Validate and apply promo code."""
        if code in self.promo_codes:
            discount = self.promo_codes[code]
            final_price = base_price * (1 - discount)
            return {
                "valid": True,
                "discount_percentage": discount * 100,
                "final_price": round(final_price, 2)
            }
        return {
            "valid": False,
            "error": "Invalid promo code"
        }

    def compare_prices(self, product_name: str) -> List[Dict[str, Union[str, float]]]:
        """Compare prices across different stores."""
        results = []
        for product in self.products:
            if product_name.lower() in product.name.lower():
                results.append({
                    "store": product.store,
                    "price": product.price,
                    "product_name": product.name
                })
        return results

    def get_return_policy(self, store: str) -> Optional[str]:
        """Get return policy for a specific store."""
        return self.return_policies.get(store)

###########################################################################################
