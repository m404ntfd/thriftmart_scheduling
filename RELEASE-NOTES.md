# Thrift Mart Dispatch 0.15.1

Move camera/library file inputs inside the active appointment dialog so mobile browsers can open the picker instead of treating the controls as inert. Regression test now opens Add photos and Use camera through the actual file chooser. Requests without street/city/ZIP no longer create an address from the default state alone. Editing older requests with an empty street does not copy the combined address into the street field.
