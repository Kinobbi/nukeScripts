(prop("Status") == "Done")
? ""
: (
    empty(prop("Due Date"))
    ? ""
    : (
        (dateBetween(prop("Due Date"), now(), "days") == 0 && day(now()) == day(prop("Due Date")))
        ? style("0 days remaining", "pink")
        : (
            (timestamp(prop("Due Date")) - timestamp(now()) > 0)
            ? (
                (dateBetween(prop("Due Date"), now(), "days") <= 5)
                ? style(
                    (dateBetween(prop("Due Date"), now(), "days") + 1 == 1)
                      ? "1 day remaining"
                      : dateBetween(prop("Due Date"), now(), "days") + 1 + " days remaining",
                    "yellow"
                  )
                : (
                    (dateBetween(prop("Due Date"), now(), "days") <= 30)
                    ? style(
                        (dateBetween(prop("Due Date"), now(), "days") + 1 == 1)
                          ? "1 day remaining"
                          : dateBetween(prop("Due Date"), now(), "days") + 1 + " days remaining",
                        "green"
                      )
                    : style(
                        (dateBetween(prop("Due Date"), now(), "days") + 1 == 1)
                          ? "1 day remaining"
                          : dateBetween(prop("Due Date"), now(), "days") + 1 + " days remaining",
                        "blue"
                      )
                  )
              )
            : style(
                (dateBetween(now(), prop("Due Date"), "days") == 1)
                  ? "1 day overdue"
                  : dateBetween(now(), prop("Due Date"), "days") + " days overdue",
                "red"
              )
        )
    )
)
