from alive_progress.animations import bar_factory, bouncing_spinner_factory

# rnpc_progress_bar = bar_factory()

rnpc_progress_spinner = (
    bouncing_spinner_factory("💚💛❤️💜💙🤍🧡🫀", 12, (2, 4)).pause(center=6).randomize()
)
