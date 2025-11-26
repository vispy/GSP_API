import datoviz as dvz

app = dvz.App()
figure = app.figure()


@app.connect(figure)
def on_keyboard(ev: dvz.KeyboardEvent):
    print(f"{ev.key_event()} key {ev.key()} ({ev.key_name()})")


app.run()
app.destroy()
