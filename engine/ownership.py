from collections import defaultdict, deque

def compute_ownership_contagion_reference(blocked_seeds, edges, max_depth=6, threshold=50.0):
    """
    Reference implementation of ownership contagion (BFS fixpoint).
    blocked_seeds: set of party_ids that are directly blocked.
    edges: list of dicts {"owner_id": X, "owned_id": Y, "pct": float}
    
    Returns: dict mapping party_id to derived_blocked status and contributors.
    """
    # Build graph: owned -> list of (owner, pct)
    graph = defaultdict(list)
    for e in edges:
        graph[e["owned_id"]].append((e["owner_id"], e["pct"]))
        
    blocked_current = set(blocked_seeds)
    derived = {}
    
    # We iterate up to max_depth times to propagate the block status
    for depth in range(max_depth):
        new_blocked = set()
        
        # Check all parties to see if their aggregate blocked ownership >= threshold
        for party, owners in graph.items():
            if party in blocked_current:
                continue # already blocked
                
            aggregate_pct = 0.0
            contributors = []
            
            for owner, pct in owners:
                if owner in blocked_current:
                    aggregate_pct += pct
                    contributors.append({"owner_id": owner, "pct": pct})
                    
            if aggregate_pct >= threshold:
                new_blocked.add(party)
                derived[party] = {
                    "total_pct": aggregate_pct,
                    "contributors": contributors,
                    "depth": depth + 1
                }
                
        if not new_blocked:
            break
            
        blocked_current.update(new_blocked)
        
    return derived

# Pathway implementation sketch (unrolled joins for safety)
# def compute_ownership_pathway(seeds, edges_cur, max_depth=6, threshold=50.0):
#     blocked = seeds
#     for _ in range(max_depth):
#         contrib = edges_cur.join(blocked, pw.left.owner_id == pw.right.party_id) \
#                            .select(owned_id=pw.left.owned_id, owner_id=pw.left.owner_id, pct=pw.left.pct)
#         agg = contrib.groupby(pw.this.owned_id).reduce(
#             party_id=pw.this.owned_id, total=pw.reducers.sum(pw.this.pct))
#         derived = agg.filter(pw.this.total >= threshold).select(party_id=pw.this.party_id)
#         blocked = blocked.concat(derived).distinct()
#     return blocked

