// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { computeDepositState, DepositStatus } from "./deposit";

const initialRecord = {
  metadata: {
    publication_date: "2022-04-01",
    title: "",
    creators: [],
  },
  files: {
    enabled: true,
  },
  status: DepositStatus.DRAFT,
  access: {
    record: "public",
    status: "metadata-only",
    embargo: {
      active: false,
    },
    files: "public",
  },
  is_published: false,
};

const fakeSelectedCommunities = [
  {
    id: "comid",
    slug: "comid",
    metadata: {
      title: "My first community",
      description: "My first community",
      type: "Type",
    },
    links: {
      self_html: "/",
    },
    ui: {
      permissions: {
        can_include_directly: false,
      },
    },
  },
  {
    id: "comid2",
    slug: "comid2",
    metadata: {
      title: "My second community",
      description: "My second community",
      type: "Type",
    },
    links: {
      self_html: "/",
    },
    ui: {
      permissions: {
        can_include_directly: false,
      },
    },
  },
  {
    id: "comid3",
    slug: "comid3",
    metadata: {
      title: "My third community",
      description: "My third community",
      type: "Type",
    },
    links: {
      self_html: "/",
    },
    ui: {
      permissions: {
        can_include_directly: true,
      },
    },
  },
  {
    id: "comid4",
    metadata: {
      title: "Deleted community",
      description: "This community is deleted.",
    },
    is_ghost: true,
    ui: {
      permissions: {
        can_include_directly: true,
      },
    },
  },
];

const savedDraftRecordNoCommunity = {
  ...initialRecord,
  id: "w7s4s-nyj77",
  parent: {
    id: "2bh62-33343",
  },
};

const savedDraftRecordWithCommunity = {
  ...initialRecord,
  id: "w7s4s-nyj77",
  status: DepositStatus.DRAFT_WITH_REVIEW,
  parent: {
    id: "2bh62-33343",
    review: {
      id: "1234",
      receiver: {
        community: fakeSelectedCommunities[0].id,
        type: "community-submission",
      },
    },
  },
  expanded: {
    parent: {
      review: {
        receiver: fakeSelectedCommunities[0],
      },
    },
  },
};

const savedDraftRecordWithDeletedCommunity = {
  ...initialRecord,
  id: "w7s4s-nyj77",
  status: DepositStatus.DRAFT_WITH_REVIEW,
  parent: {
    id: "2bh62-33343",
    review: {
      id: "1234",
      receiver: {
        community: fakeSelectedCommunities[3].id,
        type: "community-submission",
      },
    },
  },
  expanded: {
    parent: {
      review: {
        receiver: fakeSelectedCommunities[3],
      },
    },
  },
};

const submittedForReviewDraft = {
  ...savedDraftRecordWithCommunity,
  id: "w7s4s-nyj77",
  status: DepositStatus.IN_REVIEW,
};

const declinedReviewDraft = {
  ...savedDraftRecordWithCommunity,
  id: "w7s4s-nyj77",
  status: DepositStatus.DECLINED,
};

const declinedReviewDraftForDeletedCommunity = {
  ...savedDraftRecordWithDeletedCommunity,
  id: "w7s4s-nyj77",
  status: DepositStatus.DECLINED,
};

const expiredReviewDraft = {
  ...savedDraftRecordWithCommunity,
  id: "w7s4s-nyj77",
  status: DepositStatus.EXPIRED,
};

const publishedRecordInCommunity = {
  ...savedDraftRecordNoCommunity,
  status: DepositStatus.PUBLISHED,
  parent: {
    id: "2bh62-33343",
    communities: {
      default: fakeSelectedCommunities[0].id,
    },
  },
  expanded: {
    parent: {
      communities: {
        default: fakeSelectedCommunities[0],
      },
    },
  },
};

const publishedRecordInDeletedCommunity = {
  ...savedDraftRecordNoCommunity,
  status: DepositStatus.PUBLISHED,
  parent: {
    id: "2bh62-33343",
    communities: {
      default: fakeSelectedCommunities[3].id,
    },
  },
  expanded: {
    parent: {
      communities: {
        default: fakeSelectedCommunities[3],
      },
    },
  },
};

const publishedRecordWithoutCommunity = {
  ...savedDraftRecordNoCommunity,
  status: DepositStatus.PUBLISHED,
  parent: {
    id: "2bh62-33343",
  },
};

describe("Test deposit reducer", () => {
  describe("Test deposit state when no draft has been created.", () => {
    it("user selects a community", async () => {
      const expectedDepositState = {
        selectedCommunity: fakeSelectedCommunities[0],
        ui: {
          showSubmitForReviewButton: true,
          showDirectPublishButton: false,
          disableSubmitForReviewButton: false,
          showChangeCommunityButton: false,
          showCommunitySelectionButton: true,
          disableCommunitySelectionButton: false,
          showCommunityHeader: true,
        },
        actions: {
          shouldUpdateReview: true,
          shouldDeleteReview: false,
          communityStateMustBeChecked: true,
        },
      };

      expect(computeDepositState(initialRecord, fakeSelectedCommunities[0])).toEqual(
        expectedDepositState
      );
    });
    it("user selects a community (that can direct publish)", async () => {
      const expectedDepositState = {
        selectedCommunity: fakeSelectedCommunities[2],
        ui: {
          showSubmitForReviewButton: true,
          showDirectPublishButton: true,
          disableSubmitForReviewButton: false,
          showChangeCommunityButton: false,
          showCommunitySelectionButton: true,
          disableCommunitySelectionButton: false,
          showCommunityHeader: true,
        },
        actions: {
          shouldUpdateReview: true,
          shouldDeleteReview: false,
          communityStateMustBeChecked: true,
        },
      };

      expect(computeDepositState(initialRecord, fakeSelectedCommunities[2])).toEqual(
        expectedDepositState
      );
    });
    it("user deselects a community", async () => {
      const expectedDepositState = {
        selectedCommunity: null,
        ui: {
          showSubmitForReviewButton: false,
          showDirectPublishButton: false,
          disableSubmitForReviewButton: false,
          showChangeCommunityButton: false,
          showCommunitySelectionButton: true,
          disableCommunitySelectionButton: false,
          showCommunityHeader: true,
        },
        actions: {
          shouldUpdateReview: false,
          shouldDeleteReview: false,
          communityStateMustBeChecked: false,
        },
      };

      expect(computeDepositState(initialRecord, null)).toEqual(expectedDepositState);
    });
  });
  describe("Test deposit state when already a draft has been created.", () => {
    it("user selects a community and saves draft", async () => {
      const expectedDepositState = {
        selectedCommunity: fakeSelectedCommunities[0],
        ui: {
          showSubmitForReviewButton: true,
          showDirectPublishButton: false,
          disableSubmitForReviewButton: false,
          showChangeCommunityButton: false,
          showCommunitySelectionButton: true,
          disableCommunitySelectionButton: false,
          showCommunityHeader: true,
        },
        actions: {
          shouldUpdateReview: true,
          shouldDeleteReview: false,
          communityStateMustBeChecked: true,
        },
      };

      expect(
        computeDepositState(savedDraftRecordNoCommunity, fakeSelectedCommunities[0])
      ).toEqual(expectedDepositState);
    });
    it("user selects a community (that can direct publish) and saves draft", async () => {
      const expectedDepositState = {
        selectedCommunity: fakeSelectedCommunities[2],
        ui: {
          showSubmitForReviewButton: true,
          showDirectPublishButton: true,
          disableSubmitForReviewButton: false,
          showChangeCommunityButton: false,
          showCommunitySelectionButton: true,
          disableCommunitySelectionButton: false,
          showCommunityHeader: true,
        },
        actions: {
          shouldUpdateReview: true,
          shouldDeleteReview: false,
          communityStateMustBeChecked: true,
        },
      };

      expect(
        computeDepositState(savedDraftRecordNoCommunity, fakeSelectedCommunities[2])
      ).toEqual(expectedDepositState);
    });
    it("user deselects a community and saves draft", async () => {
      const expectedDepositState = {
        selectedCommunity: null,
        ui: {
          showSubmitForReviewButton: false,
          showDirectPublishButton: false,
          disableSubmitForReviewButton: false,
          showChangeCommunityButton: false,
          showCommunitySelectionButton: true,
          disableCommunitySelectionButton: false,
          showCommunityHeader: true,
        },
        actions: {
          shouldUpdateReview: false,
          shouldDeleteReview: true,
          communityStateMustBeChecked: true,
        },
      };

      expect(computeDepositState(savedDraftRecordWithCommunity, null)).toEqual(
        expectedDepositState
      );
    });
    it("user changes the selected community and saves draft", async () => {
      const expectedDepositState = {
        selectedCommunity: fakeSelectedCommunities[1],
        ui: {
          showSubmitForReviewButton: true,
          showDirectPublishButton: false,
          disableSubmitForReviewButton: false,
          showChangeCommunityButton: false,
          showCommunitySelectionButton: true,
          disableCommunitySelectionButton: false,
          showCommunityHeader: true,
        },
        actions: {
          shouldUpdateReview: true,
          shouldDeleteReview: false,
          communityStateMustBeChecked: true,
        },
      };

      expect(
        computeDepositState(savedDraftRecordWithCommunity, fakeSelectedCommunities[1])
      ).toEqual(expectedDepositState);
    });
    it("user changes the selected community (that can direct publish) and saves draft", async () => {
      const expectedDepositState = {
        selectedCommunity: fakeSelectedCommunities[2],
        ui: {
          showSubmitForReviewButton: true,
          showDirectPublishButton: true,
          disableSubmitForReviewButton: false,
          showChangeCommunityButton: false,
          showCommunitySelectionButton: true,
          disableCommunitySelectionButton: false,
          showCommunityHeader: true,
        },
        actions: {
          shouldUpdateReview: true,
          shouldDeleteReview: false,
          communityStateMustBeChecked: true,
        },
      };

      expect(
        computeDepositState(savedDraftRecordWithCommunity, fakeSelectedCommunities[2])
      ).toEqual(expectedDepositState);
    });
    it("user access a submitted for review draft", async () => {
      const expectedDepositState = {
        selectedCommunity: fakeSelectedCommunities[0],
        ui: {
          showSubmitForReviewButton: true,
          showDirectPublishButton: false,
          disableSubmitForReviewButton: true,
          showChangeCommunityButton: false,
          showCommunitySelectionButton: true,
          disableCommunitySelectionButton: true,
          showCommunityHeader: true,
        },
        actions: {
          shouldUpdateReview: false,
          shouldDeleteReview: false,
          communityStateMustBeChecked: false,
        },
      };

      expect(
        computeDepositState(submittedForReviewDraft, fakeSelectedCommunities[0])
      ).toEqual(expectedDepositState);
    });
    it("user access a declined draft. Same situation will occur if user selects again the community which request was declined", async () => {
      const expectedDepositState = {
        selectedCommunity: fakeSelectedCommunities[0],
        ui: {
          showSubmitForReviewButton: false,
          showDirectPublishButton: false,
          disableSubmitForReviewButton: false,
          showChangeCommunityButton: true,
          showCommunitySelectionButton: true,
          disableCommunitySelectionButton: true,
          showCommunityHeader: true,
        },
        actions: {
          shouldUpdateReview: false,
          shouldDeleteReview: false,
          communityStateMustBeChecked: false,
        },
      };

      expect(
        computeDepositState(declinedReviewDraft, fakeSelectedCommunities[0])
      ).toEqual(expectedDepositState);
    });

    it("user access an expired draft. Same situation will occur if user selects again the community which request expired", async () => {
      const expectedDepositState = {
        selectedCommunity: fakeSelectedCommunities[0],
        ui: {
          showSubmitForReviewButton: false,
          showDirectPublishButton: false,
          disableSubmitForReviewButton: false,
          showChangeCommunityButton: true,
          showCommunitySelectionButton: true,
          disableCommunitySelectionButton: true,
          showCommunityHeader: true,
        },
        actions: {
          shouldUpdateReview: false,
          shouldDeleteReview: false,
          communityStateMustBeChecked: false,
        },
      };

      expect(
        computeDepositState(expiredReviewDraft, fakeSelectedCommunities[0])
      ).toEqual(expectedDepositState);
    });

    it("user changes community for a declined draft and resubmits", async () => {
      const expectedDepositState = {
        selectedCommunity: fakeSelectedCommunities[1],
        ui: {
          showSubmitForReviewButton: true,
          showDirectPublishButton: false,
          disableSubmitForReviewButton: false,
          showChangeCommunityButton: false,
          showCommunitySelectionButton: true,
          disableCommunitySelectionButton: false,
          showCommunityHeader: true,
        },
        actions: {
          shouldUpdateReview: true,
          shouldDeleteReview: false,
          communityStateMustBeChecked: true,
        },
      };

      expect(
        computeDepositState(declinedReviewDraft, fakeSelectedCommunities[1])
      ).toEqual(expectedDepositState);
    });

    it("user changes community (that can direct publish) for a declined draft and resubmits", async () => {
      const expectedDepositState = {
        selectedCommunity: fakeSelectedCommunities[2],
        ui: {
          showSubmitForReviewButton: true,
          showDirectPublishButton: true,
          disableSubmitForReviewButton: false,
          showChangeCommunityButton: false,
          showCommunitySelectionButton: true,
          disableCommunitySelectionButton: false,
          showCommunityHeader: true,
        },
        actions: {
          shouldUpdateReview: true,
          shouldDeleteReview: false,
          communityStateMustBeChecked: true,
        },
      };

      expect(
        computeDepositState(declinedReviewDraft, fakeSelectedCommunities[2])
      ).toEqual(expectedDepositState);
    });

    it("user changes community for an expired draft and resubmits", async () => {
      const expectedDepositState = {
        selectedCommunity: fakeSelectedCommunities[1],
        ui: {
          showSubmitForReviewButton: true,
          showDirectPublishButton: false,
          disableSubmitForReviewButton: false,
          showChangeCommunityButton: false,
          showCommunitySelectionButton: true,
          disableCommunitySelectionButton: false,
          showCommunityHeader: true,
        },
        actions: {
          shouldUpdateReview: true,
          shouldDeleteReview: false,
          communityStateMustBeChecked: true,
        },
      };

      expect(
        computeDepositState(expiredReviewDraft, fakeSelectedCommunities[1])
      ).toEqual(expectedDepositState);
    });
  });

  it("user acces a declined draft for a community that was deleted", async () => {
    const expectedDepositState = {
      selectedCommunity: fakeSelectedCommunities[3],
      ui: {
        showSubmitForReviewButton: false,
        showDirectPublishButton: true,
        disableSubmitForReviewButton: false,
        showChangeCommunityButton: true,
        showCommunitySelectionButton: true,
        disableCommunitySelectionButton: true,
        showCommunityHeader: true,
      },
      actions: {
        shouldUpdateReview: false,
        shouldDeleteReview: false,
        communityStateMustBeChecked: false,
      },
    };

    expect(
      computeDepositState(
        declinedReviewDraftForDeletedCommunity,
        fakeSelectedCommunities[3]
      )
    ).toEqual(expectedDepositState);
  });

  it("user changes community (that can direct publish) for an expired draft and resubmits", async () => {
    const expectedDepositState = {
      selectedCommunity: fakeSelectedCommunities[1],
      ui: {
        showSubmitForReviewButton: true,
        showDirectPublishButton: false,
        disableSubmitForReviewButton: false,
        showChangeCommunityButton: false,
        showCommunitySelectionButton: true,
        disableCommunitySelectionButton: false,
        showCommunityHeader: true,
      },
      actions: {
        shouldUpdateReview: true,
        shouldDeleteReview: false,
        communityStateMustBeChecked: true,
      },
    };

    expect(computeDepositState(expiredReviewDraft, fakeSelectedCommunities[1])).toEqual(
      expectedDepositState
    );
  });

  it("user publishes without community for a declined draft", async () => {
    const expectedDepositState = {
      selectedCommunity: null,
      ui: {
        showSubmitForReviewButton: false,
        showDirectPublishButton: false,
        disableSubmitForReviewButton: false,
        showChangeCommunityButton: false,
        showCommunitySelectionButton: true,
        disableCommunitySelectionButton: false,
        showCommunityHeader: true,
      },
      actions: {
        shouldUpdateReview: false,
        shouldDeleteReview: true,
        communityStateMustBeChecked: true,
      },
    };

    expect(computeDepositState(declinedReviewDraft, null)).toEqual(
      expectedDepositState
    );
  });

  it("user accesses a published draft without community", async () => {
    const expectedDepositState = {
      selectedCommunity: null,
      ui: {
        showSubmitForReviewButton: false,
        showDirectPublishButton: false,
        disableSubmitForReviewButton: false,
        showChangeCommunityButton: false,
        showCommunitySelectionButton: false,
        disableCommunitySelectionButton: false,
        showCommunityHeader: false,
      },
      actions: {
        shouldUpdateReview: false,
        shouldDeleteReview: false,
        communityStateMustBeChecked: false,
      },
    };

    expect(computeDepositState(publishedRecordWithoutCommunity, null)).toEqual(
      expectedDepositState
    );
  });

  it("user accesses a published draft accepted in a community", async () => {
    const expectedDepositState = {
      selectedCommunity: fakeSelectedCommunities[0],
      ui: {
        showSubmitForReviewButton: false,
        showDirectPublishButton: false,
        disableSubmitForReviewButton: false,
        showChangeCommunityButton: false,
        showCommunitySelectionButton: false,
        disableCommunitySelectionButton: false,
        showCommunityHeader: true,
      },
      actions: {
        shouldUpdateReview: false,
        shouldDeleteReview: false,
        communityStateMustBeChecked: false,
      },
    };

    expect(computeDepositState(publishedRecordInCommunity, undefined)).toEqual(
      expectedDepositState
    );
  });
  it("user accesses a published draft accepted in a community that was deleted", async () => {
    const expectedDepositState = {
      selectedCommunity: fakeSelectedCommunities[3],
      ui: {
        showSubmitForReviewButton: false,
        showDirectPublishButton: false,
        disableSubmitForReviewButton: false,
        showChangeCommunityButton: false,
        showCommunitySelectionButton: false,
        disableCommunitySelectionButton: false,
        showCommunityHeader: false,
      },
      actions: {
        shouldUpdateReview: false,
        shouldDeleteReview: false,
        communityStateMustBeChecked: false,
      },
    };

    expect(computeDepositState(publishedRecordInDeletedCommunity, undefined)).toEqual(
      expectedDepositState
    );
  });
});
