from core.models import Activity, Restaurant, Hotel


class FilterEngine:

    def filter_queryset(self, model, params):
        qs = model.objects.all()

        # country filter
        if params.get("country"):
            qs = qs.filter(country__iexact=params["country"])

        # city filter
        if params.get("city"):
            qs = qs.filter(city__iexact=params["city"])

        # price filter
        if params.get("min_price") is not None:
            qs = qs.filter(base_price__gte=params["min_price"])

        if params.get("max_price") is not None:
            qs = qs.filter(base_price__lte=params["max_price"])

        # tags filter
        if params.get("tags"):
            for tag in params["tags"]:
                qs = [obj for obj in qs if tag in obj.get_tags_list()]

        return qs