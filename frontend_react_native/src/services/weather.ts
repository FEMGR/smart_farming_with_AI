import * as Location from 'expo-location';

export interface WeatherData {
  temperature: number;
  windspeed: number;
  weathercode: number;
  condition: string;
  iconName: string;
  locationName: string;
  highTemp?: number;
  lowTemp?: number;
  farmingAdvice: string;
  updatedAt: string;
}

export function getWeatherCondition(code: number): { condition: string; iconName: string; advice: string } {
  if (code === 0) {
    return {
      condition: 'Clear Sky',
      iconName: 'sun.max.fill',
      advice: 'Sunny & clear. Check soil moisture and maintain regular watering.',
    };
  }
  if (code >= 1 && code <= 3) {
    return {
      condition: 'Partly Cloudy',
      iconName: 'cloud.sun.fill',
      advice: 'Balanced sunlight. Ideal conditions for normal farm operations.',
    };
  }
  if (code === 45 || code === 48) {
    return {
      condition: 'Foggy',
      iconName: 'cloud.fog.fill',
      advice: 'High atmospheric humidity. Inspect leaves for fungal spots.',
    };
  }
  if ((code >= 51 && code <= 67) || (code >= 80 && code <= 82)) {
    return {
      condition: 'Rain Showers',
      iconName: 'cloud.rain.fill',
      advice: 'Natural rainfall detected. Pause automated irrigation routines.',
    };
  }
  if (code >= 95) {
    return {
      condition: 'Thunderstorm',
      iconName: 'cloud.bolt.rain.fill',
      advice: 'Heavy storm risk. Secure nursery plants and delicate equipment.',
    };
  }
  return {
    condition: 'Overcast',
    iconName: 'cloud.fill',
    advice: 'Mild overcast sky. Good for field maintenance and pruning.',
  };
}

export async function fetchCurrentWeather(latitude?: number, longitude?: number): Promise<WeatherData> {
  let lat = latitude;
  let lng = longitude;
  let locName = 'Farm Station';

  if (lat === undefined || lng === undefined) {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        const loc = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
        lat = loc.coords.latitude;
        lng = loc.coords.longitude;
        locName = 'GPS Location';
      }
    } catch {
      // Fallback if location permission fails or service unavailable
    }
  }

  // Default fallback coordinates if none provided
  if (lat === undefined || lng === undefined) {
    lat = 13.7563;
    lng = 100.5018;
    locName = 'Station Default';
  }

  const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lng}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&timezone=auto`;

  const res = await fetch(url);
  if (!res.ok) {
    throw new Error('Could not fetch weather data from API.');
  }

  const data = await res.json();
  const current = data.current_weather;
  const { condition, iconName, advice } = getWeatherCondition(current?.weathercode ?? 0);

  const highTemp = data.daily?.temperature_2m_max?.[0];
  const lowTemp = data.daily?.temperature_2m_min?.[0];

  return {
    temperature: Math.round(current?.temperature ?? 25),
    windspeed: Math.round(current?.windspeed ?? 10),
    weathercode: current?.weathercode ?? 0,
    condition,
    iconName,
    locationName: locName,
    highTemp: highTemp !== undefined ? Math.round(highTemp) : undefined,
    lowTemp: lowTemp !== undefined ? Math.round(lowTemp) : undefined,
    farmingAdvice: advice,
    updatedAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  };
}
