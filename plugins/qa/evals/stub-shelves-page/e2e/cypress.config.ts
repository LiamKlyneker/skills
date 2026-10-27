import { defineConfig } from "cypress";
import { seed } from "./seed";

export default defineConfig({
  e2e: {
    baseUrl: "http://127.0.0.1:4100",
    setupNodeEvents(on) {
      on("task", {
        "seed:shelf": ({ teamId, name }) => seed.shelf(teamId, name),
        "seed:archived-shelf": ({ teamId, archivedDaysAgo }) =>
          seed.archivedShelf(teamId, archivedDaysAgo),
        "seed:overdue-loan": ({ shelfId, daysOverdue }) => seed.overdueLoan(shelfId, daysOverdue),
      });
    },
  },
});
