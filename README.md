
_Team "data & pizza => insights" contribution to [Aalto Data Science Hackathon 2015](http://datasciencehackathon.cs.hut.fi/)._

# ViBE: Visual Bus Data Exploration Tool

This is a visual data exploration tool to bus delay data provided by [HSL](http://dev.hsl.fi/) in Helsinki, Finland. 

Our set of tools include: SQLite, Python, and the Google Maps Api. We also used the [gtfs_SQL_importer](https://github.com/cbick/gtfs_SQL_importer) (with minor modifications). The website design was inspired by the [auratkartalla.com](http://www.auratkartalla.com/) web pages.

## Howto

The web pages rendering the visualisations are under `site/`. The backend is built upon a set of static JSON files.

## Example

You can try out the site by pointing your browser to: [http://asolin.github.io/aalto-data-science-hackathon/](http://asolin.github.io/aalto-data-science-hackathon/).

## Copyright and License

The package is available under the GNU General Public License Version 3.0.

Below is a breakdown of the copyrights and licenses for different parts of the package.


 * For the most part:

   Copyright (c) 2015 Arno Solin, Eric Malmi, Jaakko Luttinen

   License: GPL v3


 * HTML and JS based on snowplow visualization:

   Copyright (c) 2014 Sampsa Kuronen

   License: GPL v3


 * Python script for importing GTFS to Sqlite:

   Copyright (c) 2010 Colin Bick, Robert Damphousse

   License: MIT


