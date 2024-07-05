from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class WeatherResponse(BaseModel):
    weather: str


class OutdoorSeatingResponse(BaseModel):
    outdoor_seating: str


# Dummy data for weather and outdoor seating
weather_data = {
    "munich": "Sunny, 22°C",
    "rainytown": "Rainy, 16°C",
    "sunnyville": "Sunny, 25°C",
}

outdoor_seating_data = {
    "munich": "Outdoor seating is available.",
    "rainytown": "Outdoor seating is not available.",
    "sunnyville": "Outdoor seating is available.",
}


@app.get("/weather/{city}", response_model=WeatherResponse)
async def get_weather(city: str):
    city_lower = city.lower()
    return {
        "weather": weather_data.get(city_lower, "Weather information not available")
    }


@app.get("/outdoor-seating/{city}", response_model=OutdoorSeatingResponse)
async def get_outdoor_seating(city: str):
    city_lower = city.lower()
    return {
        "outdoor_seating": outdoor_seating_data.get(
            city_lower, "Outdoor seating information not available"
        )
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5566)
