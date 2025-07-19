import os
def list_saved_signals(folder="signals"):
    if not os.path.exists(folder):
        print("📭 No signals learned yet.")
        return

    signals = [f[:-3] for f in os.listdir(folder) if f.endswith(".ir")]
    if not signals:
        print("📭 No signals found.")
    else:
        print("📋 Learned signals:")
        for name in signals:
            print(f" - {name}")


list_saved_signals()
