class FilterEngine:

    def filter_queryset(self, qs, params):

        if params.get("country"):
            qs = qs.filter(country__iexact=params["country"])

        if params.get("city"):
            qs = qs.filter(city__iexact=params["city"])

        if params.get("min_price"):
            qs = qs.filter(base_price__gte=float(params["min_price"]))

        if params.get("max_price"):
            qs = qs.filter(base_price__lte=float(params["max_price"]))

        if params.get("tags"):
            tags = params["tags"]
            qs = [obj for obj in qs if any(tag in obj.get_tags_list() for tag in tags)]

        return qs