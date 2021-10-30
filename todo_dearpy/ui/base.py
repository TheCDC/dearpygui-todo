class ComponentBase:
    @classmethod
    def callback_requires_refresh(cls, func):
        def wrapped(
            self: ComponentBase, sender, app_data: str, user_data, *args, **kwargs
        ):
            ret = func(self, sender, app_data, user_data, *args, **kwargs)
            self.refresh_ui()
            return ret

        return wrapped

    def refresh_ui(self):
        pass


class DisplayValue:
    pass
