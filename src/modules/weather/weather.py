import json
import os
from datetime import datetime
import nextcord
from nextcord import SlashOption
from nextcord.ext import commands
from geopy.geocoders import Nominatim
from astral import moon


class WeatherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.geolocator = Nominatim(user_agent="onebot 1.0")
        self.owm_token = os.environ.get("OWM_TOKEN")
        self.owm_headers = {"Accept": "text/plain"}
        self.owm_url = "https://api.openweathermap.org/data/2.5/onecall"

    # reverse lookup the location coordinates of the weather station to a town or city name
    # zoom = 14 is 'suburb' level zoom, seems most appropriate
    # the address returned is too long; take the part BEFORE the third comma (ex: Ridgewood, Queens, Queens County)
    async def coordinates_to_placename(self, latitude, longitude):
        placename = self.geolocator.reverse(
            str(latitude) + ", " + str(longitude), zoom=14, addressdetails=False
        ).address
        splitName = placename.split(",")
        if len(splitName) > 2:
            return splitName[0] + "," + splitName[1] + "," + splitName[2]
        elif len(splitName) > 1:
            return splitName[0] + "," + splitName[1]
        else:
            return splitName[0]

    # convert wind direction in degrees to friendly string
    def wind_deg_to_string(self, wind_dir):
        wind_dir += 11.25
        wind_dir = wind_dir % 360
        directions = [
            "N",
            "NNE",
            "NE",
            "ENE",
            "E",
            "ESE",
            "SE",
            "SSE",
            "S",
            "SSW",
            "SW",
            "WSW",
            "W",
            "WNW",
            "NW",
            "NNW",
        ]
        return "from the " + directions[int(wind_dir / 22.5)]

    # convert wind from meters/sec to km/hour
    def ms_to_kmh(self, wind_speed):
        return 3.6 * wind_speed

    # convert moon phase in float to emoji
    def moon_phase_to_emoji(self, phase):
        phase = int(phase)
        if phase == 0:
            return "🌑"
        if phase < 7:
            return "🌒"
        if phase == 7:
            return "🌓"
        if phase < 14:
            return "🌔"
        if phase == 14:
            return "🌕"
        if phase < 21:
            return "🌖"
        if phase == 21:
            return "🌗"
        return "🌘"

    # generate embed message
    async def generate_embed(self, weather_data_metric, weather_data_imperial):
        station_location = await self.coordinates_to_placename(
            weather_data_metric["lat"], weather_data_metric["lon"]
        )
        # 'conditions' text and corresponding icon url
        conditions = str(weather_data_metric["current"]["weather"][0]["description"])
        conditions_icon = weather_data_metric["current"]["weather"][0]["icon"]
        conditions_icon_url = "http://openweathermap.org/img/wn/" + conditions_icon + "@2x.png"
        # time data was collected, local time (also displays the timezone used)
        timezone = weather_data_metric["timezone"]
        timezone_offset = int(weather_data_metric["timezone_offset"])
        utc_timestamp = int(weather_data_metric["current"]["dt"])
        adjusted_timestamp = utc_timestamp + timezone_offset
        displayed_time = "Updated at: " + str(
            datetime.utcfromtimestamp(adjusted_timestamp).strftime("%b %d, %Y %I:%M %p ")
        )
        displayed_time += "(" + timezone + ")"
        # current, high, low temps
        temperature = "Now: " + str(int(weather_data_imperial["current"]["temp"])) + "°F "
        temperature += "(" + str(int(weather_data_metric["current"]["temp"])) + "°C)\n"
        temperature += (
            "Feels like: " + str(int(weather_data_imperial["current"]["feels_like"])) + "°F "
        )
        temperature += "(" + str(int(weather_data_metric["current"]["feels_like"])) + "°C)\n"
        temperature += "High: " + str(int(weather_data_imperial["daily"][0]["temp"]["max"])) + "°F "
        temperature += "(" + str(int(weather_data_metric["daily"][0]["temp"]["max"])) + "°C)\n"
        temperature += "Low: " + str(int(weather_data_imperial["daily"][0]["temp"]["min"])) + "°F "
        temperature += "(" + str(int(weather_data_metric["daily"][0]["temp"]["min"])) + "°C)"
        # humidity, dew point, heat index/wind chill
        humidity = "Now: " + str(int(weather_data_imperial["current"]["humidity"])) + "%\n"
        humidity += "Dew point: " + str(int(weather_data_imperial["current"]["dew_point"])) + "°F "
        humidity += "(" + str(int(weather_data_metric["current"]["dew_point"])) + "°C)"
        # wind speed and direction
        wind = (
            str(int(weather_data_imperial["current"]["wind_speed"]))
            + " mi/h ("
            + str(int(weather_data_metric["current"]["wind_speed"]))
            + " km/h)\n"
        )
        if "wind_gust" in weather_data_imperial["current"]:
            wind += "gusts "
            wind += str(int(weather_data_imperial["current"]["wind_gust"])) + " mi/h"
            if "wind_gust" in weather_data_metric["current"]:
                wind += " (" + str(int(weather_data_metric["current"]["wind_gust"])) + " km/h)"
            wind += "\n"
        wind += self.wind_deg_to_string(weather_data_imperial["current"]["wind_deg"])
        # uv, sunrise/sunset, moon phase information
        current_uv = str(round(weather_data_imperial["current"]["uvi"], 1))
        maximum_uv = str(round(weather_data_imperial["daily"][0]["uvi"], 1))
        sunrise_utc = int(weather_data_imperial["current"]["sunrise"])
        sunrise_local = sunrise_utc + timezone_offset
        sunset_utc = int(weather_data_imperial["current"]["sunset"])
        sunset_local = sunset_utc + timezone_offset
        moon_phase = moon.phase()
        moon_emoji = self.moon_phase_to_emoji(moon_phase)
        sun_moon = "UV: " + current_uv
        sun_moon += " (max: " + maximum_uv + ")\n"
        sun_moon += "Sunrise: "
        sun_moon += str(datetime.utcfromtimestamp(sunrise_local).strftime("%I:%M %p")) + "\n"
        sun_moon += "Sunset: "
        sun_moon += str(datetime.utcfromtimestamp(sunset_local).strftime("%I:%M %p")) + "\n"
        if moon_phase < 14:
            sun_moon += "moon is waxing "
        else:
            sun_moon += "moon is waning "
        sun_moon += moon_emoji
        # precipitation, if any (onecall always provides amount in mm, so must convert to Inches)
        precipitation = ""
        if "rain" in weather_data_imperial["current"]:
            if "1h" in weather_data_imperial["current"]["rain"]:
                precipitation += (
                    "Rain: "
                    + str(round(weather_data_imperial["current"]["rain"]["1h"] / 25.4, 2))
                    + "in"
                )
                precipitation += " (" + str(weather_data_metric["current"]["rain"]["1h"]) + "mm)\n"
        if "snow" in weather_data_imperial["current"]:
            if "1h" in weather_data_imperial["current"]["snow"]:
                precipitation += (
                    "Snow: "
                    + str(round(weather_data_imperial["current"]["snow"]["1h"] / 25.4, 2))
                    + "in"
                )
                precipitation += " (" + str(weather_data_metric["current"]["snow"]["1h"]) + "mm)"
        # active alerts, if any
        alerts = ""
        if "alerts" in weather_data_imperial:
            for alert in weather_data_imperial["alerts"]:
                alerts += alert["event"] + "\n"
        # create the nextcord Embed object, add data to it, and return
        embed = nextcord.Embed(
            title="Weather for " + station_location, colour=nextcord.Colour.default()
        )
        embed.set_thumbnail(url=conditions_icon_url)
        embed.add_field(name="Currently", value=conditions, inline=False)
        embed.add_field(name="Temperature", value=temperature, inline=True)
        embed.add_field(name="Humidity", value=humidity, inline=True)
        embed.add_field(name="Wind", value=wind, inline=True)
        embed.add_field(name="Sun/Moon", value=sun_moon, inline=True)
        if len(precipitation) > 0:
            embed.add_field(name="Precip. (last 1hr)", value=precipitation, inline=True)
        if len(alerts) > 0:
            embed.add_field(name="Active Alerts", value=alerts, inline=True)
        embed.set_footer(text=displayed_time)
        return embed

    @nextcord.slash_command(
        name="weather",
        description="Retrieve the current weather conditions for a specified location.",
    )
    async def weather(
        self,
        interaction: nextcord.Interaction,
        location: str = SlashOption(
            name="location",
            description="The location of the weather. If you have set a default location, you can leave this blank.",
            required=False,
        ),
        setdefault: str = SlashOption(
            name="setdefault",
            description="If you want to save this location search for later, set this to True.",
            required=False,
            choices={"True": "True"},
        ),
    ):
        user_default_location = self.bot.db_utils.get_member_pref(interaction.guild_id,
                                                                  interaction.user.id,
                                                                  "default_weather_location")
        weather_location = None
        if not location:
            if not user_default_location:
                await interaction.send("You don't have a default location set, so you need to specify a location"
                                       " using the `location` option of the slash command.",
                                       ephemeral=True,)
                return
            weather_location = user_default_location
        else:
            weather_location = location
        weather_location_coords = self.geolocator.geocode(weather_location, language="en")
        if not weather_location_coords:
            await interaction.send("Sorry, I couldn't find that location.", ephemeral=True)
            return
        # create and execute an http request to the owm onecall API, one for imperial units, one for metric
        # TODO: just do the conversion ourselves
        imperial_params = {
            "lat": weather_location_coords.latitude,
            "lon": weather_location_coords.longitude,
            "appid": self.owm_token,
            "units": "imperial",
        }
        metric_params = {
            "lat": weather_location_coords.latitude,
            "lon": weather_location_coords.longitude,
            "appid": self.owm_token,
            "units": "metric",
        }
        endpoint = "https://api.openweathermap.org/data/2.5/onecall"
        weather_data_imperial = []
        weather_data_metric = []
        async with self.bot.aiohttp_session.get(endpoint, headers=self.owm_headers, params=imperial_params) as resp:
            if resp.status != 200:
                await interaction.send("I couldn't get the weather. (Server responded with"
                                       " HTTP code " + str(resp.status) + ")",
                                       ephemeral=True,)
                self.bot.logger.error("WEATHER | OpenWeatherMap returned response code " + str(resp.status))
                return
            weather_data_imperial = json.loads(await resp.read())
        async with self.bot.aiohttp_session.get(endpoint, headers=self.owm_headers, params=metric_params) as resp:
            if resp.status != 200:
                await interaction.send("I couldn't get the weather. (Server responded with"
                                       " HTTP code " + str(resp.status) + ")",
                                       ephemeral=True,)
                self.bot.logger.error("WEATHER | OpenWeatherMap returned response code " + str(resp.status))
                return
            weather_data_metric = json.loads(await resp.read())

        # metric dataset returns the wind in meters/sec - we want km/h so lets convert
        weather_data_metric["current"]["wind_speed"] = self.ms_to_kmh(weather_data_metric["current"]["wind_speed"])
        if "wind_gust" in weather_data_metric["current"]:
            weather_data_metric["current"]["wind_gust"] = self.ms_to_kmh(weather_data_metric["current"]["wind_gust"])
        generated_embed = await self.generate_embed(weather_data_metric, weather_data_imperial)
        if location and setdefault:
            self.bot.db_utils.set_member_pref(interaction.guild_id,
                                              interaction.user.id,
                                              "default_weather_location",
                                              location)
            await interaction.send("Updated your default weather location to `" + str(location) + "`.",
                                   embed=generated_embed,)
        else:
            await interaction.send(embed=generated_embed)


def setup(bot):
    if "OWM_TOKEN" not in os.environ:
        bot.logger.error("WEATHER | OWM_TOKEN missing in your .env file! Weather module not loaded.")
        bot.logger.error("WEATHER | You need an OWM API key to use their API. https://openweathermap.org/api")
    else:
        bot.add_cog(WeatherCog(bot))
