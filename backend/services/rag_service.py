import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import numpy as np
from pydantic import BaseModel


class WeatherKnowledge(BaseModel):
    """Weather knowledge document for RAG"""
    id: str
    title: str
    content: str
    category: str = "weather_advisory"  # weather_advisory, historical_pattern, best_practice
    location: Optional[str] = None
    date_created: datetime
    tags: List[str] = []
    source: str = "system"  # system, pagasa, noah, user_upload


class RAGResult(BaseModel):
    """RAG search result"""
    content: str
    score: float
    source: str
    category: str
    location: Optional[str] = None


class RAGService:
    """RAG service for weather knowledge management using Qdrant"""
    
    def __init__(
        self, 
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "weather_knowledge"
    ):
        self.client = QdrantClient(url=qdrant_url, timeout=60)
        self.collection_name = collection_name
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight model
        self.vector_size = 384  # all-MiniLM-L6-v2 output dimension
        
        # Initialize collection
        asyncio.create_task(self._initialize_collection())
    
    async def _initialize_collection(self):
        """Initialize Qdrant collection with weather knowledge schema"""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == self.collection_name for c in collections)
            
            if not collection_exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                
                # Add default weather knowledge
                await self._populate_default_knowledge()
                
        except Exception as e:
            print(f"Error initializing collection: {e}")
    
    async def _populate_default_knowledge(self):
        """Populate collection with default weather knowledge"""
        default_knowledge = [
            WeatherKnowledge(
                id=str(uuid.uuid4()),
                title="High Humidity and Thunderstorm Formation",
                content="When humidity levels exceed 80% combined with rising temperatures, the likelihood of thunderstorm formation increases significantly. Farmers should secure outdoor equipment and avoid tall structures. Livestock should be moved to sheltered areas.",
                category="weather_advisory",
                tags=["humidity", "thunderstorms", "farming", "safety"],
                date_created=datetime.now(),
                source="system"
            ),
            WeatherKnowledge(
                id=str(uuid.uuid4()),
                title="Temperature Drop and Frost Protection",
                content="When nighttime temperatures are forecast to drop below 2°C, there is high risk of frost formation. Farmers should cover sensitive crops, drain irrigation systems, and provide additional shelter for livestock. Morning inspections are critical.",
                category="best_practice",
                tags=["frost", "temperature", "crops", "livestock"],
                date_created=datetime.now(),
                source="system"
            ),
            WeatherKnowledge(
                id=str(uuid.uuid4()),
                title="Wind Speed and Agricultural Activities",
                content="Wind speeds above 15 m/s (54 km/h) make most agricultural activities dangerous. Avoid operating tall equipment, postpone spraying activities, and secure loose materials. Harvest operations should be suspended until winds subside.",
                category="best_practice",
                tags=["wind", "farming", "safety", "equipment"],
                date_created=datetime.now(),
                source="system"
            ),
            WeatherKnowledge(
                id=str(uuid.uuid4()),
                title="Pressure Drop and Weather System Approach",
                content="A rapid atmospheric pressure drop of more than 3 hPa per hour often indicates an approaching weather system. Communities should prepare for potential severe weather including heavy rain, strong winds, or storms within 12-24 hours.",
                category="weather_advisory",
                tags=["pressure", "storms", "prediction", "preparation"],
                date_created=datetime.now(),
                source="system"
            ),
            WeatherKnowledge(
                id=str(uuid.uuid4()),
                title="Heat Index and Heat Stress Prevention",
                content="When heat index exceeds 32°C (90°F), outdoor workers and livestock face heat stress risk. Schedule heavy work for early morning or evening, ensure adequate water supply, provide shade, and monitor for heat exhaustion symptoms.",
                category="best_practice",
                tags=["heat", "temperature", "health", "livestock", "safety"],
                date_created=datetime.now(),
                source="system"
            ),
            WeatherKnowledge(
                id=str(uuid.uuid4()),
                title="Rainfall Intensity and Flood Risk",
                content="Rainfall rates exceeding 25mm per hour pose flash flood risks, especially in areas with poor drainage. Communities should clear drainage systems, avoid low-lying areas, and prepare emergency supplies. Agricultural fields may require drainage management.",
                category="weather_advisory",
                tags=["rainfall", "flooding", "drainage", "emergency"],
                date_created=datetime.now(),
                source="system"
            )
        ]
        
        for knowledge in default_knowledge:
            await self.add_knowledge(knowledge)
    
    async def add_knowledge(self, knowledge: WeatherKnowledge) -> bool:
        """Add weather knowledge to the RAG database"""
        try:
            # Create embedding
            embedding = self.encoder.encode(knowledge.content)
            
            # Prepare point for Qdrant
            point = PointStruct(
                id=knowledge.id,
                vector=embedding.tolist(),
                payload={
                    "title": knowledge.title,
                    "content": knowledge.content,
                    "category": knowledge.category,
                    "location": knowledge.location,
                    "date_created": knowledge.date_created.isoformat(),
                    "tags": knowledge.tags,
                    "source": knowledge.source
                }
            )
            
            # Insert into Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            return True
            
        except Exception as e:
            print(f"Error adding knowledge: {e}")
            return False
    
    async def search_knowledge(
        self,
        query: str,
        limit: int = 5,
        category_filter: Optional[str] = None,
        location_filter: Optional[str] = None
    ) -> List[RAGResult]:
        """Search weather knowledge using semantic similarity"""
        try:
            # Create query embedding
            query_embedding = self.encoder.encode(query)
            
            # Prepare search filters - Use proper Qdrant models
            search_filter = None
            if category_filter or location_filter:
                from qdrant_client.http import models
                conditions = []

                if category_filter:
                    conditions.append(
                        models.FieldCondition(
                            key="category",
                            match=models.MatchValue(value=category_filter)
                        )
                    )

                if location_filter:
                    conditions.append(
                        models.FieldCondition(
                            key="location",
                            match=models.MatchValue(value=location_filter)
                        )
                    )

                if conditions:
                    search_filter = models.Filter(must=conditions)
            
            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                query_filter=search_filter,
                limit=limit,
                with_payload=True
            )
            
            # Convert to RAGResult objects
            results = []
            for result in search_results:
                rag_result = RAGResult(
                    content=result.payload.get("content", ""),
                    score=result.score,
                    source=result.payload.get("source", "unknown"),
                    category=result.payload.get("category", "unknown"),
                    location=result.payload.get("location")
                )
                results.append(rag_result)
            
            return results
            
        except Exception as e:
            print(f"Error searching knowledge: {e}")
            return []
    
    async def get_contextual_knowledge(
        self,
        weather_condition: str,
        location: Optional[str] = None,
        audience: str = "general"  # farmers, officials, general
    ) -> List[RAGResult]:
        """Get relevant knowledge based on current weather conditions"""
        
        # Create context-aware query
        audience_context = {
            "farmers": "agricultural farming crop livestock",
            "officials": "disaster emergency community safety",
            "general": "daily activities safety preparation"
        }
        
        enhanced_query = f"{weather_condition} {audience_context.get(audience, '')}"
        
        if location:
            enhanced_query += f" {location}"
        
        # Search with multiple strategies
        results = []
        
        # 1. Direct weather condition search
        direct_results = await self.search_knowledge(enhanced_query, limit=3)
        results.extend(direct_results)
        
        # 2. Category-specific search for audience
        if audience == "farmers":
            farming_results = await self.search_knowledge(
                weather_condition, 
                limit=2, 
                category_filter="best_practice"
            )
            results.extend(farming_results)
        
        # 3. Advisory search
        advisory_results = await self.search_knowledge(
            weather_condition,
            limit=2,
            category_filter="weather_advisory"
        )
        results.extend(advisory_results)
        
        # Remove duplicates and sort by relevance
        unique_results = {}
        for result in results:
            if result.content not in unique_results or result.score > unique_results[result.content].score:
                unique_results[result.content] = result
        
        return sorted(unique_results.values(), key=lambda x: x.score, reverse=True)[:5]
    
    async def add_historical_pattern(
        self,
        location: str,
        pattern_description: str,
        weather_data: Dict[str, Any],
        outcome: str
    ) -> bool:
        """Add historical weather pattern for future reference"""
        
        knowledge = WeatherKnowledge(
            id=str(uuid.uuid4()),
            title=f"Historical Pattern: {location}",
            content=f"Weather Pattern: {pattern_description}\nData: {weather_data}\nOutcome: {outcome}\nLocation: {location}",
            category="historical_pattern",
            location=location,
            tags=["historical", "pattern", location.lower()],
            date_created=datetime.now(),
            source="system"
        )
        
        return await self.add_knowledge(knowledge)
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge collection"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            # Get category distribution
            category_counts = {}
            
            # Scroll through all points to get category stats
            points, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=1000,  # Assuming we have less than 1000 documents
                with_payload=True
            )
            
            for point in points:
                category = point.payload.get("category", "unknown")
                category_counts[category] = category_counts.get(category, 0) + 1
            
            return {
                "total_documents": collection_info.points_count,
                "vector_dimension": collection_info.config.params.vectors.size,
                "category_distribution": category_counts,
                "collection_name": self.collection_name
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def close(self):
        """Close the Qdrant client connection"""
        if hasattr(self.client, 'close'):
            self.client.close()