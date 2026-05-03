from django.db.models import Q

class FilterEngine:

    def filter_queryset(self, qs, params):
        # Location filters
        if params.get("country"):
            qs = qs.filter(country__iexact=params["country"])
        if params.get("city"):
            qs = qs.filter(city__iexact=params["city"])

        # Numeric ranges
        if params.get("min_price"):
            qs = qs.filter(price__gte=float(params["min_price"]))
        if params.get("max_price"):
            qs = qs.filter(price__lte=float(params["max_price"]))
        
        if params.get("max_duration"):
            qs = qs.filter(duration__lte=float(params["max_duration"]))

        # Dynamic Category Filtering (for Activity JSON lists)
        selected_categories = params.getlist("category")
        if selected_categories:
            cat_filter = Q()
            for cat in selected_categories:
                # Matches if the JSON list contains the category
                cat_filter |= Q(category__contains=cat)
            qs = qs.filter(cat_filter)

        # Global search
        if params.get("q"):
            query = params.get("q")
            qs = qs.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )

        return qs.distinct()