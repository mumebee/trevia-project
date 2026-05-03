from django.db.models import Q

class BaseFilterEngine:
    """Base class for shared filtering logic."""
    def filter_common(self, qs, params):
        # Global text search
        if params.get("q"):
            query = params.get("q")
            qs = qs.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )

        # Location filters
        selected_countries = params.getlist("country")
        if selected_countries:
            qs = qs.filter(country__in=selected_countries)

        selected_cities = params.getlist("city")
        if selected_cities:
            qs = qs.filter(city__in=selected_cities)

        # Numeric ranges
        try:
            if params.get("min_price"):
                qs = qs.filter(price__gte=float(params["min_price"]))
            if params.get("max_price"):
                qs = qs.filter(price__lte=float(params["max_price"]))
        except ValueError:
            pass # Handle non-numeric input gracefully

        return qs

class ActivityFilterEngine(BaseFilterEngine):
    def filter_queryset(self, qs, params):
        qs = self.filter_common(qs, params)

        # Duration filter
        if params.get("max_duration"):
            try:
                qs = qs.filter(duration__lte=float(params["max_duration"]))
            except ValueError:
                pass

        # Tag filtering using the 'tags' CharField (SQLite friendly)
        selected_tags = params.getlist("tags")
        if selected_tags:
            cat_filter = Q()
            for tag in selected_tags:
                cat_filter |= Q(tags__icontains=tag)
            qs = qs.filter(cat_filter)

        return qs.distinct()

class RestaurantFilterEngine(BaseFilterEngine):
    def filter_queryset(self, qs, params):
        qs = self.filter_common(qs, params)
        
        if params.get("cuisine"):
            qs = qs.filter(cuisine_type__icontains=params.get("cuisine"))
            
        return qs.distinct()

class HotelFilterEngine(BaseFilterEngine):
    def filter_queryset(self, qs, params):
        qs = self.filter_common(qs, params)
        
        if params.get("stars"):
            try:
                qs = qs.filter(stars__gte=int(params.get("stars")))
            except ValueError:
                pass
        return qs.distinct()